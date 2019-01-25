package edu.stanford.nlp.coref;

import java.io.*;
import java.util.*;
import java.util.logging.Logger;

import edu.stanford.nlp.coref.data.CorefChain;
import edu.stanford.nlp.coref.data.CorefCluster;
import edu.stanford.nlp.coref.data.Dictionaries;
import edu.stanford.nlp.coref.data.Document;
import edu.stanford.nlp.coref.data.DocumentMaker;
import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.pipeline.Annotation;
import edu.stanford.nlp.util.Generics;
import edu.stanford.nlp.util.Pair;
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
        BufferedWriter bw = new BufferedWriter(
            new FileWriter(
                new File(args[0] + ".coref.out")
            )
        );
        StringBuilder os = new StringBuilder();

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
//        System.out.println("---");
//        System.out.println("coref chains");

        HashMap<Integer, String> idToCharacter = new HashMap<>();

        for (CorefChain cc : document.get(CorefCoreAnnotations.CorefChainAnnotation.class).values()) {
            System.out.println("\t" + cc);
            idToCharacter.put(cc.getChainID(), cc.character);
        }

        int i = 1;

        System.err.println(idToCharacter);

        HashSet<String> characters = new HashSet<>();

        for (CoreMap sentence : document.get(CoreAnnotations.SentencesAnnotation.class)) {
            System.out.println("---");
            System.out.println("sentence " + String.valueOf(i) + ": ");
            System.out.println(sentence.get(CoreAnnotations.TextAnnotation.class));
//            System.out.println(sentence);
            System.out.println("mentions: ");

            if (sentence.get(CorefCoreAnnotations.CorefMentionsAnnotation.class).size() == 0) {
                String text = sentence.get(CoreAnnotations.TextAnnotation.class);

                if (text.equals("# .")) {
                    os.append("\n");
                } else if (text.endsWith(" # .")) {
                    os.append(text, 0, text.lastIndexOf(" # ."));
                    os.append("\n");
                } else {
                    os.append(sentence + " ");
                }

                continue;
            }

            ArrayList<String> words = null;
            ArrayList<Pair<Pair<Integer, Integer>, String>> replacements = new ArrayList<>();
            StringBuilder replacedSentence = new StringBuilder();

            for (Mention m : sentence.get(CorefCoreAnnotations.CorefMentionsAnnotation.class)) {
                int id = m.corefClusterID;
                String character = "";

                if (words == null) {
                    words = new ArrayList<String>() {};
                    for (CoreLabel word: m.sentenceWords) {
                        words.add(
                            word.get(CoreAnnotations.TextAnnotation.class)
                        );
                    }
                    System.out.println(words);
                }

//                System.err.println(id);

                if (idToCharacter.containsKey(id)) {
                    character = idToCharacter.get(id);
                    System.err.println(String.valueOf(id) + " - " + character);

                    if (!character.equals("")) {
                        replacements.add(new Pair<>(new Pair<>(m.startIndex, m.endIndex), character));
                    }
                }

                System.out.printf("\t" + m + " (%d, %d) [" + character + " = ]", m.startIndex, m.endIndex);
            }

            replacements.sort(
                Comparator.comparingInt(o -> o.first.first)
            );

            int currIdx = 0;

            for (Pair<Pair<Integer, Integer>, String> replacement: replacements) {
                while (currIdx < replacement.first.first) {
//                    if (words.get(currIdx).equals("#")) {
//                        System.err.println(words);
//                        System.err.println(words.get(currIdx + 1).equals("."));
//                    }

                    if (words.get(currIdx).equals("#")
                        && (currIdx + 1 < words.size() && words.get(currIdx + 1).equals("."))) {
                        replacedSentence.append("\n");
                        currIdx += 2;
                    } else {
                        replacedSentence.append(words.get(currIdx)).append(" ");
                        currIdx += 1;
                    }
//                    replacedSentence.append(" ");
//                    replacedSentence.append(words.get(currIdx) + " ");
                }
                if (replacement.first.first + 1 == replacement.first.second) {
                    replacedSentence.append(words.get(replacement.first.first)).append(" ");

//                    if (replacement.first.first > 0) {
//                        replacedSentence.append(" ");
//                    }
                } else {
                    for (int j = replacement.first.first; j < replacement.first.second; ++j) {
                        replacedSentence.append(words.get(j));

                        if (j < replacement.first.second - 1) {
                            replacedSentence.append("_");
                        }
                    }

                    replacedSentence.append(" ");
                }
                characters.add("($_" + replacement.second + ")");
                replacedSentence.append("($_").append(replacement.second).append(") ");

                currIdx = replacement.first.second;
            }

            while (currIdx < words.size()) {
                if (words.get(currIdx).equals("#")
                    && (currIdx + 1 < words.size() && words.get(currIdx + 1).equals("."))) {
                    replacedSentence.append("\n");
                    currIdx += 2;
                } else {
                    replacedSentence.append(words.get(currIdx)).append(" ");
                    currIdx += 1;
                }
            }

            os.append(replacedSentence.toString());

//            System.out.println(replacements);

            i += 1;
        }

        bw.write(os.toString());
        bw.flush();

        BufferedWriter cw = new BufferedWriter(
            new FileWriter(
                new File(args[0] + ".chars")
            )
        );
        StringBuilder csb = new StringBuilder();

        for (String c: characters) {
            csb.append(c + "\n");
        }

        cw.write(csb.toString());
        cw.flush();

//        System.out.println("coref chains with character");
//        for (CorefChain cc : document.get(CorefCoreAnnotations.CorefChainAnnotation.class).values()) {
//            if (!cc.character.equals("")) {
//                System.out.println("\t" + cc.character + ": " + cc);
//            }
//        }

//        return;

//        Properties props = StringUtils.argsToProperties(args);
//        CorefSystem coref = new CorefSystem(props);
//        coref.runOnConll(props);
    }
}
