package edu.stanford.nlp.coref;

import java.io.*;
import java.util.Calendar;
import java.util.Map;
import java.util.Properties;
import java.util.logging.Logger;

import edu.stanford.nlp.coref.data.CorefChain;
import edu.stanford.nlp.coref.data.CorefCluster;
import edu.stanford.nlp.coref.data.Dictionaries;
import edu.stanford.nlp.coref.data.Document;
import edu.stanford.nlp.coref.data.DocumentMaker;
import edu.stanford.nlp.pipeline.Annotation;
import edu.stanford.nlp.util.Generics;
import edu.stanford.nlp.util.StringUtils;
import edu.stanford.nlp.util.logging.Redwood;


import edu.stanford.nlp.coref.CorefCoreAnnotations;
import edu.stanford.nlp.coref.data.CorefChain;
import edu.stanford.nlp.coref.data.Mention;
import edu.stanford.nlp.ling.CoreAnnotations;
import edu.stanford.nlp.pipeline.Annotation;
import edu.stanford.nlp.pipeline.StanfordCoreNLP;
import edu.stanford.nlp.util.CoreMap;

/**
 * Class for running coreference algorithms
 *
 * @author Kevin Clark
 */
public class CorefSystem {
    private final DocumentMaker docMaker;
    private final CorefAlgorithm corefAlgorithm;
    private final boolean removeSingletonClusters;
    private final boolean verbose;

    public CorefSystem(Properties props) {
        try {
            Dictionaries dictionaries = new Dictionaries(props);
            docMaker = new DocumentMaker(props, dictionaries);
            corefAlgorithm = CorefAlgorithm.fromProps(props, dictionaries);
            removeSingletonClusters = CorefProperties.removeSingletonClusters(props);
            verbose = CorefProperties.verbose(props);
        } catch (Exception e) {
            throw new RuntimeException("Error initializing coref system", e);
        }
    }

    public CorefSystem(DocumentMaker docMaker, CorefAlgorithm corefAlgorithm,
                       boolean removeSingletonClusters, boolean verbose) {
        this.docMaker = docMaker;
        this.corefAlgorithm = corefAlgorithm;
        this.removeSingletonClusters = removeSingletonClusters;
        this.verbose = verbose;
    }

    public void annotate(Annotation ann) {
        Document document;
        try {
            document = docMaker.makeDocument(ann);
        } catch (Exception e) {
            throw new RuntimeException("Error making document", e);
        }

        CorefUtils.checkForInterrupt();
        corefAlgorithm.runCoref(document);
        if (removeSingletonClusters) {
            CorefUtils.removeSingletonClusters(document);
        }
        CorefUtils.checkForInterrupt();

        Map<Integer, CorefChain> result = Generics.newHashMap();
        for (CorefCluster c : document.corefClusters.values()) {
            result.put(c.clusterID, new CorefChain(c, document.positions));
        }
        ann.set(CorefCoreAnnotations.CorefChainAnnotation.class, result);
    }

    public void runOnConll(Properties props) throws Exception {
        String baseName = CorefProperties.conllOutputPath(props) +
            Calendar.getInstance().getTime().toString().replaceAll("\\s", "-").replaceAll(":", "-");
        String goldOutput = baseName + ".gold.txt";
        String beforeCorefOutput = baseName + ".predicted.txt";
        String afterCorefOutput = baseName + ".coref.predicted.txt";
        PrintWriter writerGold = new PrintWriter(new FileOutputStream(goldOutput));
        PrintWriter writerBeforeCoref = new PrintWriter(new FileOutputStream(beforeCorefOutput));
        PrintWriter writerAfterCoref = new PrintWriter(new FileOutputStream(afterCorefOutput));

        (new CorefDocumentProcessor() {
            @Override
            public void process(int id, Document document) {
                writerGold.print(CorefPrinter.printConllOutput(document, true));
                writerBeforeCoref.print(CorefPrinter.printConllOutput(document, false));
                long time = System.currentTimeMillis();
                corefAlgorithm.runCoref(document);
                if (verbose) {
                    Redwood.log(getName(), "Coref took "
                        + (System.currentTimeMillis() - time) / 1000.0 + "s");
                }
                CorefUtils.removeSingletonClusters(document);
                writerAfterCoref.print(CorefPrinter.printConllOutput(document, false, true));
            }

            @Override
            public void finish() throws Exception {
            }

            @Override
            public String getName() {
                return corefAlgorithm.getClass().getName();
            }
        }).run(docMaker);

        Logger logger = Logger.getLogger(CorefSystem.class.getName());
        String summary = CorefScorer.getEvalSummary(CorefProperties.getScorerPath(props),
            goldOutput, beforeCorefOutput);
        CorefScorer.printScoreSummary(summary, logger, false);
        summary = CorefScorer.getEvalSummary(CorefProperties.getScorerPath(props), goldOutput,
            afterCorefOutput);
        CorefScorer.printScoreSummary(summary, logger, true);
        CorefScorer.printFinalConllScore(summary);

        writerGold.close();
        writerBeforeCoref.close();
        writerAfterCoref.close();
    }

    public static void main(String[] args) throws Exception {
//        Annotation document = new Annotation("Barack Obama was born in Hawaii.  He is the president. Obama was elected in 2008.");
//        Annotation document = new Annotation("Chandler tugs his scarf tighter around his neck, " +
//            "conscious of the little red love bites Joey left on his throat the night before. " +
//            "He loves the crisp chill of the December air in the city, the steam rising from a hot cup of coffee, " +
//            "and the layers upon layers of clothing required to keep warm. Joey’s not a big fan of layers, " +
//            "which Chandler absolutely approves of, because that means less work for him when they get back to the apartment " +
//            "and undress each other with frantic hands.");

        File file = new File(args[0]);

        BufferedReader br = new BufferedReader(new FileReader(file));

        String st;
        StringBuffer sb = new StringBuffer();
        while ((st = br.readLine()) != null) {
//            System.out.println(st);
            sb.append(st);
        }
//    }

//        Annotation document = new Annotation("They make their way through the rest of the presents—homemade brownies from Monica, oatmeal cookies and therapeutic bath salts from Phoebe (Chandler wonders if Joey let it slip to Phoebe about their, uh, shared bathtime). Ross gives Joey a ridiculously large shark pillow that’s clearly from the museum gift shop, and Chandler a Star Trek pajama set—complete with Tribble slippers. Rachel gifts Chandler a set of teas and coffee blends from Central Perk, and Joey gets gift passes to various restaurants.\n" +
//            "Joey’s practically vibrating with anticipation as Chandler slides the final two gifts over to him. “Open the big one first,” Chandler says, and Joey is not going to argue with that. He rips open the paper like Wolverine on a bad day, then his face goes through a complicated series of emotions when he sees what’s inside: a Sony PlayStation.\n" +
//            "Chandler doesn’t have time to decode all the various expressions on Joey’s face, because Joey’s pulling him in and kissing his mouth over and over. “Oh, man, I have the best boyfriend ever! You’re amazing, and I’m so sorry I ever said you were crappy!”");

        Annotation document = new Annotation(sb.toString());
        Properties props = new Properties();
        props.setProperty("annotators", "tokenize,ssplit,pos,lemma,ner,parse,coref");
        StanfordCoreNLP pipeline = new StanfordCoreNLP(props);
        pipeline.annotate(document);
        System.out.println("---");
        System.out.println("coref chains");
        for (CorefChain cc : document.get(CorefCoreAnnotations.CorefChainAnnotation.class).values()) {
            System.out.println("\t" + cc);
        }
        for (CoreMap sentence : document.get(CoreAnnotations.SentencesAnnotation.class)) {
            System.out.println("---");
            System.out.println("mentions");
            for (Mention m : sentence.get(CorefCoreAnnotations.CorefMentionsAnnotation.class)) {
                System.out.println("\t" + m);
            }
        }

        return;

//        Properties props = StringUtils.argsToProperties(args);
//        CorefSystem coref = new CorefSystem(props);
//        coref.runOnConll(props);
    }
}
