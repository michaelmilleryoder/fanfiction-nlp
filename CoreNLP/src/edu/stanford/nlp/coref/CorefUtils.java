package edu.stanford.nlp.coref;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import edu.stanford.nlp.coref.data.CorefCluster;
import edu.stanford.nlp.coref.data.Dictionaries;
import edu.stanford.nlp.coref.data.Document;
import edu.stanford.nlp.coref.data.Mention;
import edu.stanford.nlp.ling.CoreAnnotations;
import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.util.Pair;
import edu.stanford.nlp.util.RuntimeInterruptedException;

/**
 * Useful utilities for coreference resolution.
 * @author Kevin Clark
 */
public class CorefUtils {
  public static List<Mention> getSortedMentions(Document document) {
    List<Mention> mentions = new ArrayList<>(document.predictedMentionsByID.values());
    Collections.sort(mentions, (m1, m2) -> m1.appearEarlierThan(m2) ? -1 : 1);
    return mentions;
  }

  public static List<Pair<Integer, Integer>> getMentionPairs(Document document) {
     List<Pair<Integer, Integer>> pairs = new ArrayList<>();
     List<Mention> mentions = getSortedMentions(document);
     for (int i = 0; i < mentions.size(); i++) {
       for (int j = 0; j < i; j++) {
         pairs.add(new Pair<>(mentions.get(j).mentionID, mentions.get(i).mentionID));
       }
     }
     return pairs;
   }

   public static Map<Pair<Integer, Integer>, Boolean> getUnlabeledMentionPairs(Document document) {
     return CorefUtils.getMentionPairs(document).stream()
         .collect(Collectors.toMap(p -> p, p -> false));
   }

   public static Map<Pair<Integer, Integer>, Boolean> getLabeledMentionPairs(Document document) {
     Map<Pair<Integer, Integer>, Boolean> mentionPairs = getUnlabeledMentionPairs(document);
     for (CorefCluster c : document.goldCorefClusters.values()) {
       List<Mention> clusterMentions = new ArrayList<>(c.getCorefMentions());
       for (Mention clusterMention : clusterMentions) {
         for (Mention clusterMention2 : clusterMentions) {
           Pair<Integer, Integer> mentionPair = new Pair<>(
               clusterMention.mentionID, clusterMention2.mentionID);
           if (mentionPairs.containsKey(mentionPair)) {
             mentionPairs.put(mentionPair, true);
           }
         }
       }
     }
     return mentionPairs;
   }

  public static void mergeCoreferenceClusters(Pair<Integer, Integer> mentionPair,
      Document document) {
    Mention m1 = document.predictedMentionsByID.get(mentionPair.first);
    Mention m2 = document.predictedMentionsByID.get(mentionPair.second);
//    System.out.println("merging " + m1 + " with " + m2);
    if (m1.corefClusterID == m2.corefClusterID) {
      return;
    }

//    if (m1.isPronominal()) {
//      System.err.println(m1);
//      System.err.println(m1.gender);
////      System.exit(0);
//    }

    int removeId = m1.corefClusterID;
    CorefCluster c1 = document.corefClusters.get(m1.corefClusterID);

//    if (m1.toString().equals("Phoebe")) {
//      System.out.println("it's Phoebe!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!");
//      System.out.println(m1.gender);
//      System.out.println(m1.mentionType);
//    }
//
//    if (m1.toString().equals("Kathy")) {
//      System.out.println("it's Kathy!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!");
//      System.out.println(m1.gender);
//      System.out.println(m1.mentionType);
//    }
//
//    if (m2.toString().equals("Kathy")) {
//      System.out.println("it's Kathy!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!");
//      System.out.println(m2.gender);
//      System.out.println(m2.mentionType);
//    }

//    System.out.println("cluster c1 of m1 is represented by " + c1.representative);
//    System.out.println("first mention is " + c1.getFirstMention());
//    System.out.println(c1 + "=" + c1.clusterID + "with gender" + c1.gender);

    CorefCluster c2 = document.corefClusters.get(m2.corefClusterID);

//    if (m2.toString().equals("Phoebe")) {
//      System.out.println("it's Phoebe!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!");
//      System.out.println(m2.gender);
//      System.out.println(m2.mentionType);
//    }
//
//    System.out.println("cluster c2 of m2 is represented by " + c2.representative);
//    System.out.println("first mention is " + c2.getFirstMention());
//    System.out.println(c2 + "=" + c2.clusterID + "with gender" + c2.gender);





//    if (m1.toString().equals("Chandler")) {
//      System.out.println("it's Chandler!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!");
//      System.out.println(m1.gender);
//    }
//
//    if (m1.toString().equals("Joey")) {
//      System.out.println("it's Joey!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!");
//      System.out.println(m1.gender);
//    }

//    if ((c1.words.contains("chandler") && c2.words.contains("joey"))
//        || (c2.words.contains("chandler") && c1.words.contains("joey"))) {
//      System.out.println("wrong merging!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!");
//    } else
    int a;



    if (!c1.character.isEmpty() && !c2.character.isEmpty()
        && !(c1.character.contains(c2.character) || c2.character.contains(c1.character))
    ) {
//      System.out.println("wrong merging based on character!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!");
//      System.out.println("c1 with character " + c1.character);
//      System.out.println("c2 with character " + c2.character);
      a = 0;
    } else if ((c1.gender.equals(Dictionaries.Gender.FEMALE) && c2.gender.equals(Dictionaries.Gender.MALE))
        || (c2.gender.equals(Dictionaries.Gender.FEMALE) && c1.gender.equals(Dictionaries.Gender.MALE))) {
//      System.out.println("wrong merging based on gender!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!");
//      System.out.println(m1 + " with gender " + m1.gender + " with cluster gender " + c1.gender);
//      System.out.println(m2 + " with gender " + m2.gender + " with cluster gender " + c2.gender);
      a = 0;
    } else {
      CorefCluster.mergeClusters(c2, c1);
      document.corefClusters.remove(removeId);
//      System.out.println("after merging, c2.character = " + c2.character);
    }
  }

  public static void removeSingletonClusters(Document document) {
    for (CorefCluster c : new ArrayList<>(document.corefClusters.values())) {
      if (c.getCorefMentions().size() == 1) {
        document.corefClusters.remove(c.clusterID);
      }
    }
  }

  public static void checkForInterrupt() {
    if (Thread.interrupted()) {
      throw new RuntimeInterruptedException();
    }
  }

  public static Map<Integer, List<Integer>> heuristicFilter(List<Mention> sortedMentions,
      int maxMentionDistance, int maxMentionDistanceWithStringMatch) {
    Map<String, List<Mention>> wordToMentions = new HashMap<>();
    for (int i = 0; i < sortedMentions.size(); i++) {
      Mention m = sortedMentions.get(i);
      for (String word : getContentWords(m)) {
        wordToMentions.putIfAbsent(word, new ArrayList<>());
        wordToMentions.get(word).add(m);
      }
    }

    Map<Integer, List<Integer>> mentionToCandidateAntecedents = new HashMap<>();
    for (int i = 0; i < sortedMentions.size(); i++) {
      Mention m = sortedMentions.get(i);
      List<Integer> candidateAntecedents = new ArrayList<>();
      for (int j = Math.max(0, i - maxMentionDistance); j < i; j++) {
        candidateAntecedents.add(sortedMentions.get(j).mentionID);
      }
      for (String word : getContentWords(m)) {
        List<Mention> withStringMatch = wordToMentions.get(word);
        if (withStringMatch != null) {
          for (Mention match : withStringMatch) {
            if (match.mentionNum < m.mentionNum
                && match.mentionNum >= m.mentionNum - maxMentionDistanceWithStringMatch) {
              if (!candidateAntecedents.contains(match.mentionID)) {
                candidateAntecedents.add(match.mentionID);
              }
            }
          }
        }
      }
      if (!candidateAntecedents.isEmpty()) {
        mentionToCandidateAntecedents.put(m.mentionID, candidateAntecedents);
      }
    }
    return mentionToCandidateAntecedents;
  }

  private static List<String> getContentWords(Mention m) {
    List<String> words = new ArrayList<>();
    for (int i = m.startIndex; i < m.endIndex; i++) {
      CoreLabel cl = m.sentenceWords.get(i);
      String POS = cl.get(CoreAnnotations.PartOfSpeechAnnotation.class);
      if (POS.equals("NN") || POS.equals("NNS") || POS.equals("NNP") || POS.equals("NNPS")) {
        words.add(cl.word().toLowerCase());
      }
    }
    return words;
  }
}
