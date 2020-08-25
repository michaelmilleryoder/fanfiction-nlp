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

//        System.out.println("Tokens\n");

        // Extract character names based on ner tags as an addition
        // Removed since it's tricky to directly add them the mentions for coref
        // (which is extracted by edu.stanford.nlp.coref.md.DependencyCorefMentionFinder)
//        for (CoreMap sentence : doc.annotation.get(CoreAnnotations.SentencesAnnotation.class)) {
//
//            ArrayList<CoreLabel> tokens = new ArrayList<>();
//
//            for (CoreLabel token : sentence.get(CoreAnnotations.TokensAnnotation.class)) {
//                tokens.add(token);
//                System.out.println(
//                    token.get(CoreAnnotations.TextAnnotation.class)
//                        + " " + token.get(CoreAnnotations.NamedEntityTagAnnotation.class)
//
//                );
//            }
//
//            for (int i = 0; i < tokens.size(); ++i) {
//                CoreLabel token = tokens.get(i);
//                if (isPersonOrOrg(token)) {
//                    String mwe = "";
//                    mwe += getWord(token) + " ";
//
//                    for (int j = i + 1; j < tokens.size(); j++) {
//                        CoreLabel next = tokens.get(j);
//                        if (isPersonOrOrg(next)) {
//                            mwe += getWord(tokens.get(j)) + " ";
//                            i = j;
//                        } else {
//                            break;
//                        }
//                    }
//
//                    String name = mwe.trim();
//
//                    perDocNerCharacterCounts.put(
//                        name, perDocNerCharacterCounts.getOrDefault(name, 0) + 1
//                    );
//
//                }
//            }
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

        File textsDir = new File("../" + args[0]);

        File charListsDir = new File(args[1]);

        File outputsDir = new File(args[2]);
        
        Properties props = new Properties();
        props.setProperty("annotators", "tokenize,ssplit,pos,lemma,ner,parse,coref");
		props.setProperty("tokenize.whitespace", "true");
        StanfordCoreNLP pipeline = new StanfordCoreNLP(props);
        String textFilename;

        File[] textFiles = textsDir.listFiles();
        System.err.println(String.valueOf(textFiles.length) + " files found");
//        int gc_cnt = 0, max_gc_cnt = 50;

        // Process all texts in textsDir
        for (File textFile : textFiles) {
            textFilename = textFile.getName();

            // Check if the file is already processed
            File charListOutput = new File(charListsDir.getPath() + "/" + textFilename + ".chars");
            if (charListOutput.exists()) {
            	System.err.println("Already processed " + textFilename);
            	continue;
            }

            // If not, process
            System.err.println("processing " + textFilename);

            try {
                BufferedReader reader = new BufferedReader(new FileReader(textFile));
                StringBuilder textBuilder = new StringBuilder();
                String s;

                while ((s = reader.readLine()) != null) {
                    textBuilder.append(s);
                }

                Annotation document = new Annotation(textBuilder.toString());

                // Run the annotation pipeline on entire document
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


                // Merging character names as post-processing
                for (int i = 0; i < ids.size(); ++i) {
                    for (int j = i + 1; j < ids.size(); ++j) {
                        int id1 = ids.get(i), id2 = ids.get(j);
                        String character1 = idToCharacter.get(id1), character2 = idToCharacter.get(id2);

                        if (character1.contains(character2)) {
                            idToCharacter.put(id2, character1);
                        } else if (character2.contains(character1)) {
                            idToCharacter.put(id1, character2);
                        } else if (character1.toLowerCase().equals(character2.toLowerCase())) {
                        	idToCharacter.put(id2, character1);
                        }
                    }
                }

                int i = 1;


                HashSet<String> characters = new HashSet<>();

                // Add the character tags to the text and process the paragraph delimiter "# ."
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
//                    StringBuilder replacedSentence = new StringBuilder(); // new sentence with modifications

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
                        }

                        if (idToCharacter.containsKey(id)) {
                            character = idToCharacter.get(id);

                             String processedChar = String.join("_", character.split(" ")).replaceAll("[,\\.\\!\\? \\h']", "").replaceAll("_+", "_").replaceAll("^_", "").replaceAll("_$", "");
                            if (!character.equals("")) {
                                replacements.add(
                                    new Pair<>(
                                        new Pair<>(m.startIndex, m.endIndex),
                                        //String.join("_", character.split(" "))
                                        processedChar
                                    )
                                );
                            }
                        }

                    }

                    replacements.sort(
                        Comparator.comparingInt(o -> o.first.first)
                    );

                    List<String> replacedWords = new ArrayList<>(words); // new sentence tokens with modifications, joined to a string at end

                    for (Pair<Pair<Integer, Integer>, String> replacement : replacements) {
                    	
                    		String begin_tag = "<character name=\"" + replacement.second + "\">"; 
                    		String end_tag = "</character>"; 
                    		
                    		String taggedWord = ""; // placeholder for word to add
                    	
						// Add <character name=name>mention</character> tags (apostrophe s exclude from mention)
                        if (replacement.first.first + 1 == replacement.first.second) { // 1-word mention
                        		taggedWord = begin_tag + replacedWords.get(replacement.first.first) + end_tag;
                        		replacedWords.set(replacement.first.first, taggedWord);

                        } else { // multi-word mention
                        	
                        	// begin-tag first word
                        	taggedWord = begin_tag + replacedWords.get(replacement.first.first);
                        	replacedWords.set(replacement.first.first, taggedWord);
                        	
                        	// end-tag after last word
                        if (words.get(replacement.first.second - 1).equals("'s")) {
                        		taggedWord = replacedWords.get(replacement.first.second - 2) + end_tag;
                            replacedWords.set(replacement.first.second - 2, taggedWord);

                         } else {
                        		taggedWord = replacedWords.get(replacement.first.second - 1) + end_tag;
                            replacedWords.set(replacement.first.second - 1, taggedWord);
                         }

                        }

                        characters.add(replacement.second);

                    }

                    String replacedSentence = String.join(" ", replacedWords) + " ";
                    // Replace # . to paragraph breaks
                    replacedSentence = replacedSentence.replaceAll("# \\.", "\n");

                    outputBuilder.append(replacedSentence.toString());

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

//                for (HashMap.Entry<String, Integer> entry : perDocNerCharacterCounts.entrySet()) {
//
//                    String name = String.join("_", entry.getKey().split(" "));
//                    name = "($_" + name + ")";
//
//                    characters.add(name);
//                }

                for (String c : characters) {
                    charListBuilder.append(c).append("\n");
                }

                charListWriter.write(charListBuilder.toString());
                charListWriter.flush();
                charListWriter.close();

//                ++gc_cnt;

//                if (gc_cnt == max_gc_cnt) {
//                    System.gc();
//                    gc_cnt = 0;
//                }

            } catch (Exception e) {
                PrintWriter errorWriter = new PrintWriter(
                    new FileWriter(
                        new File(textFilename + ".error"), true
                    )
                );

                e.printStackTrace(errorWriter);
                errorWriter.close();

            }

        }

    }
}
