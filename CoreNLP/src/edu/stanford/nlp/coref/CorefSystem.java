package edu.stanford.nlp.coref;

import java.io.*;
import java.util.*;
import java.util.logging.Logger;

import edu.stanford.nlp.coref.data.*;
import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.pipeline.Annotation;
import edu.stanford.nlp.util.Generics;
import edu.stanford.nlp.util.Pair;
import edu.stanford.nlp.util.logging.Redwood;


import edu.stanford.nlp.coref.data.CorefChain;
import edu.stanford.nlp.ling.CoreAnnotations;
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
    private static HashMap<String, Integer> perDocNerCharacterCounts;

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

    Boolean isPersonOrOrg(CoreLabel token) {
        String ne = token.get(CoreAnnotations.NamedEntityTagAnnotation.class);
        return ne.equals("PERSON") || ne.equals("ORGANIZATION");
    }

    String getWord(CoreLabel token) {
        return token.get(CoreAnnotations.TextAnnotation.class);
    }

    public void annotate(Annotation ann) {
        Document document;
        try {
            document = docMaker.makeDocument(ann);
        } catch (Exception e) {
            throw new RuntimeException("Error making document", e);
        }

        InputDoc doc = new InputDoc(ann);
        perDocNerCharacterCounts = new HashMap<>();

        System.out.println("Tokens\n");

        for (CoreMap sentence : doc.annotation.get(CoreAnnotations.SentencesAnnotation.class)) {
//            mentions.add(sentence.get(CorefCoreAnnotations.CorefMentionsAnnotation.class));

            ArrayList<CoreLabel> tokens = new ArrayList<>();

            for (CoreLabel token : sentence.get(CoreAnnotations.TokensAnnotation.class)) {
                tokens.add(token);
                System.out.println(
                    token.get(CoreAnnotations.TextAnnotation.class)
                        + " " + token.get(CoreAnnotations.NamedEntityTagAnnotation.class)

                );
            }

            for (int i = 0; i < tokens.size(); ++i) {
                CoreLabel token = tokens.get(i);
                if (isPersonOrOrg(token)) {
                    String mwe = "";
                    mwe += getWord(token) + " ";

                    for (int j = i + 1; j < tokens.size(); j++) {
                        CoreLabel next = tokens.get(j);
                        if (isPersonOrOrg(next)) {
                            mwe += getWord(tokens.get(j)) + " ";
                            i = j;
                        } else {
                            break;
                        }
                    }

                    String name = mwe.trim();

//                    System.out.println(name + " " + i);

                    perDocNerCharacterCounts.put(
                        name, perDocNerCharacterCounts.getOrDefault(name, 0) + 1
                    );

//                    characterHash.add(name);
//                    int count = 0;
//                    if (counts.containsKey(name)) {
//                        count = counts.get(name);
//                    }
//                    count++;
//                    counts.put(name, count);
                }
            }
        }

//        for (HashMap.Entry<String, Integer> entry : perDocNerCharacterCounts.entrySet()) {
//            System.out.println(entry);
//        }


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


        File textsDir = new File("../" + args[0]);
//        textsDir.mkdir();

        File charListsDir = new File(args[1]);
//        charListsDir.mkdir();

        File outputsDir = new File(args[2]);
//        outputsDir.mkdir();

//        File file = new File(args[0]);

        Properties props = new Properties();
        props.setProperty("annotators", "tokenize,ssplit,pos,lemma,ner,parse,coref");
        StanfordCoreNLP pipeline = new StanfordCoreNLP(props);
        String textFilename;

//        System.err.println(charListsDir.getName());
//        System.err.println(charListsDir.getPath());
//
//        System.err.println(outputsDir.getName());
//        System.err.println(outputsDir.getPath());

        File[] textFiles = textsDir.listFiles();
        System.err.println(String.valueOf(textFiles.length) + " files found");

        for (File textFile : textFiles) {
//            System.err.println(textFile.getName());
//            System.err.println(textFile.getPath());
            textFilename = textFile.getName();
            System.err.println("processing " + textFilename);

            try {


                BufferedReader reader = new BufferedReader(new FileReader(textFile));
                StringBuilder textBuilder = new StringBuilder();
                String s;

                while ((s = reader.readLine()) != null) {
                    textBuilder.append(s);
                }

                Annotation document = new Annotation(textBuilder.toString());
                pipeline.annotate(document);

                StringBuilder outputBuilder = new StringBuilder();

                BufferedWriter outputWriter = new BufferedWriter(
                    new FileWriter(
                        new File(outputsDir.getPath() + "/" + textFilename + ".coref.txt")
                    )
                );

                HashMap<Integer, String> idToCharacter = new HashMap<>();
                ArrayList<Integer> ids = new ArrayList<>();


                for (CorefChain cc : document.get(CorefCoreAnnotations.CorefChainAnnotation.class).values()) {
                    if (!cc.character.equals("")) {
                        idToCharacter.put(cc.getChainID(), cc.character);
                        ids.add(cc.getChainID());
                    }
                }

                for (int i = 0; i < ids.size(); ++i) {
                    for (int j = i + 1; j < ids.size(); ++j) {
                        int id1 = ids.get(i), id2 = ids.get(j);
                        String character1 = idToCharacter.get(id1), character2 = idToCharacter.get(id2);

                        if (character1.contains(character2)) {
                            idToCharacter.put(id2, character1);
                        } else if (character2.contains(character1)) {
                            idToCharacter.put(id1, character2);
                        }
                    }
                }

                int i = 1;


                HashSet<String> characters = new HashSet<>();

                for (CoreMap sentence : document.get(CoreAnnotations.SentencesAnnotation.class)) {
                    if (sentence.get(CorefCoreAnnotations.CorefMentionsAnnotation.class).size() == 0) {
                        String text = sentence.get(CoreAnnotations.TextAnnotation.class);

                        if (text.equals("# .")) {
                            outputBuilder.append("\n");
                        } else if (text.endsWith(" # .")) {
                            outputBuilder.append(text, 0, text.lastIndexOf(" # ."));
                            outputBuilder.append("\n");
                        } else {
                            outputBuilder.append(sentence).append(" ");
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
                            words = new ArrayList<String>() {
                            };
                            for (CoreLabel word : m.sentenceWords) {
                                words.add(
                                    word.get(CoreAnnotations.TextAnnotation.class)
                                );
                            }
//                    System.out.println(words);
                        }

//                System.err.println(id);

                        if (idToCharacter.containsKey(id)) {
                            character = idToCharacter.get(id);
//                    System.err.println(String.valueOf(id) + " - " + character);

                            if (!character.equals("")) {
                                replacements.add(
                                    new Pair<>(
                                        new Pair<>(m.startIndex, m.endIndex),
                                        String.join("_", character.split(" "))
                                    )
                                );
                            }
                        }

//                System.out.printf("\t" + m + " (%d, %d) [" + character + " = ]", m.startIndex, m.endIndex);
                    }

                    replacements.sort(
                        Comparator.comparingInt(o -> o.first.first)
                    );

                    int currIdx = 0;

                    for (Pair<Pair<Integer, Integer>, String> replacement : replacements) {
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

                        boolean hasApostropheS = false;

                        if (replacement.first.first + 1 == replacement.first.second) {
                            replacedSentence.append(words.get(replacement.first.first)).append(" ");

//                    if (replacement.first.first > 0) {
//                        replacedSentence.append(" ");
//                    }
                        } else {
                            for (int j = replacement.first.first; j < replacement.first.second; ++j) {
                                if (j == replacement.first.second - 1 && words.get(j).equals("'s")) {
                                    hasApostropheS = true;
                                    break;
                                }

                                if (j > replacement.first.first) {
                                    replacedSentence.append("_");
                                }

                                replacedSentence.append(words.get(j));
                            }

                            replacedSentence.append(" ");
                        }
                        characters.add("($_" + replacement.second + ")");
                        replacedSentence.append("($_").append(replacement.second).append(") ");

                        if (hasApostropheS) {
                            replacedSentence.append("'s").append(" ");
                        }

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

                    outputBuilder.append(replacedSentence.toString());

//            System.out.println(replacements);

                    i += 1;
                }

                outputWriter.write(outputBuilder.toString());
                outputWriter.flush();
                outputWriter.close();

                BufferedWriter charListWriter = new BufferedWriter(
                    new FileWriter(
                        new File(charListsDir.getPath() + "/" + textFilename + ".chars")
                    )
                );
                StringBuilder charListBuilder = new StringBuilder();

                for (HashMap.Entry<String, Integer> entry : perDocNerCharacterCounts.entrySet()) {
//                System.out.println(entry);
                    String name = String.join("_", entry.getKey().split(" "));
                    name = "($_" + name + ")";

                    characters.add(name);
                }

                for (String c : characters) {
                    charListBuilder.append(c).append("\n");
                }

                charListWriter.write(charListBuilder.toString());
                charListWriter.flush();
                charListWriter.close();
            } catch (Exception e) {
//                System.err.println("error during running " + textFilename);
//                System.err.println(e);
                PrintWriter errorWriter = new PrintWriter(
                    new FileWriter(
                        new File(textFilename + ".error"), true
                    )
                );

                e.printStackTrace(errorWriter);
                errorWriter.close();

//                errorWriter.write(e.getMessage());
            }

        }


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
