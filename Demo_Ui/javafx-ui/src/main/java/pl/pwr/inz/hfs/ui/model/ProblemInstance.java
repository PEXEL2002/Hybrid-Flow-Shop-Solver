package pl.pwr.inz.hfs.ui.model;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

import java.util.Arrays;

/**
 * Model danych reprezentujący instancję problemu harmonogramowania HFS-SDST.
 *
 * Zawiera wszystkie dane wejściowe potrzebne do rozwiązania problemu,
 * w tym czasy przetwarzania, czasy przezbrojeń oraz parametry uczenia.
 */
public class ProblemInstance {

    private String algorithm;
    private int num_stages;
    private int num_jobs;
    private int[] machines_per_stage;
    private double learning_coefficient;
    private String learning_stages;
    private double[][][] processing_times;
    private double[][][][] setup_times;

    /**
     * Konstruktor domyślny.
     */
    public ProblemInstance() {
    }

    /**
     * Konstruktor parametryczny.
     *
     * @param algorithm Typ algorytmu ("bnb", "greedy", "tabu")
     * @param numStages Liczba etapów
     * @param numJobs Liczba zadań
     * @param machinesPerStage Liczba maszyn na każdym etapie
     * @param learningCoefficient Współczynnik uczenia (α)
     * @param learningStages String binarny określający etapy z uczeniem
     */
    public ProblemInstance(String algorithm, int numStages, int numJobs,
                          int[] machinesPerStage, double learningCoefficient,
                          String learningStages) {
        this.algorithm = algorithm;
        this.num_stages = numStages;
        this.num_jobs = numJobs;
        this.machines_per_stage = machinesPerStage;
        this.learning_coefficient = learningCoefficient;
        this.learning_stages = learningStages;

        initializeArrays();
    }

    /**
     * Inicjalizuje tablice czasów przetwarzania i przezbrojeń.
     */
    private void initializeArrays() {
        processing_times = new double[num_jobs][num_stages][];
        for (int j = 0; j < num_jobs; j++) {
            for (int s = 0; s < num_stages; s++) {
                processing_times[j][s] = new double[machines_per_stage[s]];
            }
        }

        setup_times = new double[num_jobs][num_jobs][num_stages][];
        for (int i = 0; i < num_jobs; i++) {
            for (int j = 0; j < num_jobs; j++) {
                for (int s = 0; s < num_stages; s++) {
                    setup_times[i][j][s] = new double[machines_per_stage[s]];
                }
            }
        }
    }
    public String getAlgorithm() {
        return algorithm;
    }

    public void setAlgorithm(String algorithm) {
        this.algorithm = algorithm;
    }

    public int getNumStages() {
        return num_stages;
    }

    public void setNumStages(int num_stages) {
        this.num_stages = num_stages;
    }

    public int getNumJobs() {
        return num_jobs;
    }

    public void setNumJobs(int num_jobs) {
        this.num_jobs = num_jobs;
    }

    public int[] getMachinesPerStage() {
        return machines_per_stage;
    }

    public void setMachinesPerStage(int[] machines_per_stage) {
        this.machines_per_stage = machines_per_stage;
    }

    public double getLearningCoefficient() {
        return learning_coefficient;
    }

    public void setLearningCoefficient(double learning_coefficient) {
        this.learning_coefficient = learning_coefficient;
    }

    public String getLearningStages() {
        return learning_stages;
    }

    public void setLearningStages(String learning_stages) {
        this.learning_stages = learning_stages;
    }

    public double[][][] getProcessingTimes() {
        return processing_times;
    }

    public void setProcessingTimes(double[][][] processing_times) {
        this.processing_times = processing_times;
    }

    public double[][][][] getSetupTimes() {
        return setup_times;
    }

    public void setSetupTimes(double[][][][] setup_times) {
        this.setup_times = setup_times;
    }

    /**
     * Konwertuje obiekt do formatu JSON.
     *
     * @return String reprezentujący obiekt w formacie JSON
     */
    public String toJson() {
        Gson gson = new GsonBuilder().setPrettyPrinting().create();
        return gson.toJson(this);
    }

    /**
     * Tworzy obiekt ProblemInstance z ciągu JSON.
     *
     * @param json String w formacie JSON
     * @return Instancja ProblemInstance
     */
    public static ProblemInstance fromJson(String json) {
        Gson gson = new Gson();
        return gson.fromJson(json, ProblemInstance.class);
    }

    /**
     * Waliduje poprawność danych instancji problemu.
     *
     * @return true jeśli dane są poprawne, false w przeciwnym razie
     */
    public boolean isValid() {
        if (num_stages <= 0 || num_jobs <= 0) return false;
        if (machines_per_stage == null || machines_per_stage.length != num_stages) return false;
        if (learning_coefficient < 0 || learning_coefficient > 1) return false;
        if (learning_stages == null || learning_stages.length() != num_stages) return false;
        if (processing_times == null || setup_times == null) return false;

        return true;
    }

    @Override
    public String toString() {
        return "ProblemInstance{" +
                "algorithm='" + algorithm + '\'' +
                ", num_stages=" + num_stages +
                ", num_jobs=" + num_jobs +
                ", machines_per_stage=" + Arrays.toString(machines_per_stage) +
                ", learning_coefficient=" + learning_coefficient +
                ", learning_stages='" + learning_stages + '\'' +
                '}';
    }
}
