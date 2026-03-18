package pl.pwr.inz.hfs.ui.model;

import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;

import java.lang.reflect.Type;
import java.util.List;

/**
 * Model wyników harmonogramowania.
 *
 * Reprezentuje strukturę wyników zwracaną przez backend Python,
 * zawierającą harmonogram operacji oraz metryki wydajności.
 */
public class ScheduleResult {

    private double time_in_ms;
    private String Algorithm;
    private String gant_diagram;
    private double C_max;
    private List<Operation> schedule;

    /**
     * Konstruktor domyślny.
     */
    public ScheduleResult() {
    }

    /**
     * Konstruktor parametryczny.
     *
     * @param time_in_ms Czas wykonania w milisekundach
     * @param algorithm Nazwa algorytmu
     * @param gant_diagram Ścieżka do diagramu Gantta
     * @param C_max Maksymalny czas zakończenia (makespan)
     * @param schedule Lista operacji w harmonogramie
     */
    public ScheduleResult(double time_in_ms, String algorithm, String gant_diagram, double C_max, List<Operation> schedule) {
        this.time_in_ms = time_in_ms;
        this.Algorithm = algorithm;
        this.gant_diagram = gant_diagram;
        this.C_max = C_max;
        this.schedule = schedule;
    }

    public double getTimeInMs() {
        return time_in_ms;
    }

    public void setTimeInMs(double time_in_ms) {
        this.time_in_ms = time_in_ms;
    }

    public double getTime() {
        return time_in_ms;
    }

    public void setTime(double time) {
        this.time_in_ms = time;
    }

    public String getAlgorithm() {
        return Algorithm;
    }

    public void setAlgorithm(String algorithm) {
        this.Algorithm = algorithm;
    }

    public String getGantDiagram() {
        return gant_diagram;
    }

    public void setGantDiagram(String gant_diagram) {
        this.gant_diagram = gant_diagram;
    }

    public double getCMaxValue() {
        return C_max;
    }

    public void setCMaxValue(double C_max) {
        this.C_max = C_max;
    }

    public List<Operation> getSchedule() {
        return schedule;
    }

    public void setSchedule(List<Operation> schedule) {
        this.schedule = schedule;
    }

    /**
     * Oblicza i zwraca maksymalny czas zakończenia (Cmax).
     *
     * Jeśli wartość C_max jest dostępna, zwraca ją. W przeciwnym razie
     * oblicza maksymalny czas zakończenia z listy operacji.
     *
     * @return Maksymalny czas zakończenia
     */
    public double getCmax() {
        if (C_max > 0) {
            return C_max;
        }
        if (schedule == null || schedule.isEmpty()) {
            return 0.0;
        }
        return schedule.stream()
                .mapToDouble(Operation::getEnd)
                .max()
                .orElse(0.0);
    }

    /**
     * Tworzy obiekt ScheduleResult z ciągu JSON.
     *
     * @param json String w formacie JSON
     * @return Instancja ScheduleResult
     */
    public static ScheduleResult fromJson(String json) {
        Gson gson = new Gson();
        return gson.fromJson(json, ScheduleResult.class);
    }

    /**
     * Klasa reprezentująca pojedynczą operację w harmonogramie.
     *
     * Może być operacją przetwarzania zadania lub operacją przezbrojenia.
     */
    public static class Operation {
        private String type;
        private Integer job;
        private Integer from_job;
        private Integer to_job;
        private int stage;
        private int machine;
        private double start;
        private double end;

        /**
         * Konstruktor domyślny.
         */
        public Operation() {
        }

        public String getType() {
            return type;
        }

        public void setType(String type) {
            this.type = type;
        }

        public Integer getJob() {
            return job;
        }

        public void setJob(Integer job) {
            this.job = job;
        }

        public Integer getFromJob() {
            return from_job;
        }

        public void setFromJob(Integer from_job) {
            this.from_job = from_job;
        }

        public Integer getToJob() {
            return to_job;
        }

        public void setToJob(Integer to_job) {
            this.to_job = to_job;
        }

        public int getStage() {
            return stage;
        }

        public void setStage(int stage) {
            this.stage = stage;
        }

        public int getMachine() {
            return machine;
        }

        public void setMachine(int machine) {
            this.machine = machine;
        }

        public double getStart() {
            return start;
        }

        public void setStart(double start) {
            this.start = start;
        }

        public double getEnd() {
            return end;
        }

        public void setEnd(double end) {
            this.end = end;
        }

        public double getDuration() {
            return end - start;
        }

        @Override
        public String toString() {
            if ("operation".equals(type)) {
                return String.format("Job %d, Stage %d, Machine %d: [%.2f - %.2f]",
                        job, stage, machine, start, end);
            } else {
                return String.format("Setup %d→%d, Stage %d, Machine %d: [%.2f - %.2f]",
                        from_job, to_job, stage, machine, start, end);
            }
        }
    }

    @Override
    public String toString() {
        return String.format("ScheduleResult{time=%.3fs, Cmax=%.2f, operations=%d}",
                time_in_ms / 1000.0, getCmax(), schedule != null ? schedule.size() : 0);
    }
}
