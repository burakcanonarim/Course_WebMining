import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.io.RandomAccessFile;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

/*
 * Author is @Burak Can Onarım, student of Muğla Sıtkı Koçman University,
 * Department of Computer Engineering. This is my Apriori Algorithm and
 * created to do first web mining homework in 2020.
 * 
 * Input file that is called 'transactions1.txt' or 'transactions2.txt'.
 * Transactions are shown line by line.
 * Items in transactions are listed by side and separated by comma. 
 */

public class Apriori {
    // 'minimumSupport' and 'textFile' variables can change by User
    private static double minimumSupport = 0.4;
    private static String textFile = "Web Mining Workspace/transactions3.txt";

    // 'maxLine' and 'transactions' variables can change by automatically
    private static int maxLine = getMaxNumberOfLines(textFile);
    private static String[][] transactions;

    public static void main(String[] args) throws IOException {
        // Assign the transactions
        transactions = readFileIntoMultiDimensionalArray(textFile);

        // The transactions join into one array
        ArrayList<String> totalItemList = new ArrayList<>();
        for (int i = 0; i < maxLine; i++) {
            totalItemList.addAll(Arrays.asList(transactions[i]));
        }

        System.out.println("File of " + textFile + "\nWith " + minimumSupport
                + " support value, Set of Frequent 1-itemset is: " + Arrays.deepToString(
                        convertArrayListToMultiDimensionalArray(frequentOneItemset(countFrequencies(totalItemList)))));

    }

    /*
     * To read from text file with separated by comma and add all elements item by
     * item into the 'dynamic' multidimensional array
     */
    public static String[][] readFileIntoMultiDimensionalArray(String inputFile) throws IOException {
        RandomAccessFile file = new RandomAccessFile(inputFile, "r");
        String line;
        String[][] readFile = new String[maxLine][];

        int i = 0;
        while ((line = file.readLine()) != null && i < maxLine) {
            readFile[i] = line.split(",");
            i++;
        }
        file.close();

        return readFile;
    }

    // To get that how many lines -transactions- are there in dataset.
    public static int getMaxNumberOfLines(String inputFile) {
        int maxNumberOfLines = 0;

        try (BufferedReader br = new BufferedReader(new FileReader(inputFile))) {
            while ((br.readLine()) != null) {
                maxNumberOfLines++;
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return maxNumberOfLines;
    }

    // This method is 'init-pass' in Pseudo Code
    public static Map<String, Double> countFrequencies(ArrayList<String> list) {
        Map<String, Double> countList = new HashMap<String, Double>();

        for (String item : list) {
            Double count = countList.get(item);
            countList.put(item, (count == null) ? 1 : count + 1);
        }
        return countList;
    }

    public static ArrayList<String> frequentOneItemset(Map<String, Double> map) {
        ArrayList<String> frequentItemList = new ArrayList<>();

        for (Map.Entry<String, Double> val : map.entrySet()) {
            double itemSupport = val.getValue() / maxLine;
            if (minimumSupport <= itemSupport) {
                frequentItemList.add(val.getKey());
            }
        }
        // To sort according to lexicographic order
        frequentItemList.sort(null);

        return frequentItemList;
    }

    public static String[][] convertArrayListToMultiDimensionalArray(ArrayList<String> arrayList) {
        String[][] myMDArray = new String[arrayList.size()][];

        for (int i = 0; i < arrayList.size(); i++) {
            ArrayList<String> subList = new ArrayList<>();
            subList.add(arrayList.get(i));
            myMDArray[i] = new String[subList.size()];

            for (int j = 0; j < subList.size(); j++) {
                myMDArray[i][j] = subList.get(j);
            }
        }

        return myMDArray;
    }

}
