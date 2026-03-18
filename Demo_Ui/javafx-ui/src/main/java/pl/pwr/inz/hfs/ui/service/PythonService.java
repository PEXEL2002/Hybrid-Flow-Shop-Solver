package pl.pwr.inz.hfs.ui.service;

import pl.pwr.inz.hfs.ui.model.ProblemInstance;
import pl.pwr.inz.hfs.ui.model.ScheduleResult;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.concurrent.TimeUnit;

/**
 * Serwis komunikacji z backendem Python.
 *
 * Zarządza uruchamianiem skryptów Python poprzez ProcessBuilder
 * oraz wymianą danych przez pliki JSON.
 */
public class PythonService {

    private static final String PYTHON_EXECUTABLE = "python";
    private static final String MAIN_SCRIPT = "main.py";
    private static final int TIMEOUT_SECONDS = 600;

    private final String pythonProjectPath;
    private final String dataDir;
    private final String resultsDir;

    /**
     * Konstruktor serwisu Python.
     *
     * @param pythonProjectPath Ścieżka do katalogu projektu Python
     * @throws IllegalArgumentException Gdy ścieżka nie istnieje
     */
    public PythonService(String pythonProjectPath) {
        this.pythonProjectPath = pythonProjectPath;
        Path pythonPath = Paths.get(pythonProjectPath);
        Path rootPath = pythonPath.getParent();
        this.dataDir = rootPath.resolve("data").toString();
        this.resultsDir = rootPath.resolve("results").toString();

        if (!Files.exists(pythonPath)) {
            throw new IllegalArgumentException("Ścieżka do projektu Python nie istnieje: " + pythonProjectPath);
        }

        try {
            Files.createDirectories(Paths.get(dataDir));
            Files.createDirectories(Paths.get(resultsDir));
        } catch (Exception e) {
            System.err.println("Nie można utworzyć katalogów data/results: " + e.getMessage());
        }
    }

    /**
     * Uruchamia algorytm optymalizacji dla podanej instancji problemu.
     *
     * Tworzy plik JSON z danymi, uruchamia skrypt Python
     * i zwraca wyniki harmonogramowania.
     *
     * @param instance Instancja problemu do rozwiązania
     * @return Wyniki harmonogramowania
     * @throws Exception W przypadku błędu walidacji lub wykonania
     */
    public ScheduleResult runOptimization(ProblemInstance instance) throws Exception {
        if (!instance.isValid()) {
            throw new IllegalArgumentException("Uszkodzony plik wejściowy .json\n\n" +
                    "Plik zawiera nieprawidłową strukturę danych.\n" +
                    "Sprawdź poprawność wprowadzonych danych.");
        }

        String inputFileName = "input_" + System.currentTimeMillis() + ".json";
        Path inputFilePath = Paths.get(dataDir, inputFileName);
        Files.createDirectories(Paths.get(dataDir));
        Files.writeString(inputFilePath, instance.toJson());

        String algorithm = instance.getAlgorithm();
        Path outputFilePath = Paths.get(resultsDir, "result.json");

        ProcessBuilder processBuilder = new ProcessBuilder();
        processBuilder.command(
                PYTHON_EXECUTABLE,
                MAIN_SCRIPT,
                inputFilePath.toString()
        );
        processBuilder.directory(new File(pythonProjectPath));
        processBuilder.redirectErrorStream(true);

        Process process = processBuilder.start();

        StringBuilder output = new StringBuilder();

        try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()))) {
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line).append("\n");
            }
        }

        boolean finished = process.waitFor(TIMEOUT_SECONDS, TimeUnit.SECONDS);

        if (!finished) {
            process.destroyForcibly();
            throw new Exception("Przekroczono limit czasu wykonania.\n\n" +
                    "Spróbuj zmniejszyć liczbę zadań lub wybrać szybszy algorytm (np. Greedy).");
        }

        int exitCode = process.exitValue();
        if (exitCode != 0) {
            throw new Exception("Uszkodzony plik wejściowy .json\n\n" +
                    "Sprawdź, czy plik zawiera poprawne dane:\n" +
                    "- Liczba zadań i etapów musi być większa od 0\n" +
                    "- Czasy wykonania muszą być liczbami dodatnimi\n" +
                    "- Struktura pliku musi być zgodna z formatem JSON");
        }

        if (!Files.exists(outputFilePath)) {
            throw new Exception("Uszkodzony plik wejściowy .json\n\n" +
                    "Nie udało się wygenerować harmonogramu.\n" +
                    "Sprawdź poprawność danych wejściowych.");
        }

        String resultJson = Files.readString(outputFilePath);
        ScheduleResult result;
        try {
            result = ScheduleResult.fromJson(resultJson);
        } catch (Exception e) {
            throw new Exception("Uszkodzony plik wejściowy .json\n\n" +
                    "Dane wejściowe zawierają błędy, które uniemożliwiły przetworzenie.");
        }

        return result;
    }

    /**
     * Sprawdza czy Python jest dostępny w systemie.
     *
     * Uruchamia komendę 'python --version' i sprawdza czy zakończyła się sukcesem.
     *
     * @return true jeśli Python jest zainstalowany i dostępny, false w przeciwnym razie
     */
    public static boolean isPythonAvailable() {
        try {
            ProcessBuilder pb = new ProcessBuilder(PYTHON_EXECUTABLE, "--version");
            Process process = pb.start();
            boolean finished = process.waitFor(5, TimeUnit.SECONDS);
            return finished && process.exitValue() == 0;
        } catch (Exception e) {
            return false;
        }
    }

    /**
     * Pobiera wersję zainstalowanego Pythona.
     *
     * Uruchamia komendę 'python --version' i zwraca wynik jako string.
     *
     * @return Wersja Pythona (np. "Python 3.10.5") lub komunikat o błędzie
     */
    public static String getPythonVersion() {
        try {
            ProcessBuilder pb = new ProcessBuilder(PYTHON_EXECUTABLE, "--version");
            Process process = pb.start();
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            String version = reader.readLine();
            process.waitFor(5, TimeUnit.SECONDS);
            return version != null ? version : "Nieznana";
        } catch (Exception e) {
            return "Błąd: " + e.getMessage();
        }
    }

    /**
     * Zwraca ścieżkę do katalogu z wynikami.
     *
     * @return Bezwzględna ścieżka do katalogu results/
     */
    public String getResultsDir() {
        return resultsDir;
    }

    /**
     * Zwraca ścieżkę do wykresu Gantta dla danego algorytmu.
     *
     * @param algorithm Nazwa algorytmu (np. "Greedy", "Tabu-Search")
     * @return Ścieżka do pliku PNG z wykresem Gantta
     */
    public Path getGanttChartPath(String algorithm) {
        return Paths.get(resultsDir, algorithm + "_gantt.png");
    }

    /**
     * Generuje wykres Gantta dla istniejącego pliku z harmonogramem.
     *
     * Uruchamia skrypt Python z parametrem --gantt, który generuje
     * wizualizację harmonogramu i zapisuje ścieżkę do pliku PNG w JSON.
     *
     * @param scheduleFilePath Ścieżka do pliku JSON z harmonogramem
     * @return Ścieżka do wygenerowanego wykresu Gantta
     * @throws Exception W przypadku błędu wykonania lub nieprawidłowych danych
     */
    public Path generateGanttChart(String scheduleFilePath) throws Exception {
        Path schedulePath = Paths.get(scheduleFilePath);
        if (!Files.exists(schedulePath)) {
            throw new Exception("Uszkodzony plik wejściowy .json\n\n" +
                    "Podany plik harmonogramu nie istnieje lub został usunięty.");
        }

        ProcessBuilder processBuilder = new ProcessBuilder();
        processBuilder.command(
                PYTHON_EXECUTABLE,
                MAIN_SCRIPT,
                "--gantt",
                scheduleFilePath
        );
        processBuilder.directory(new File(pythonProjectPath));
        processBuilder.redirectErrorStream(true);

        Process process = processBuilder.start();

        StringBuilder output = new StringBuilder();

        try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()))) {
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line).append("\n");
            }
        }

        boolean finished = process.waitFor(TIMEOUT_SECONDS, TimeUnit.SECONDS);

        if (!finished) {
            process.destroyForcibly();
            throw new Exception("Przekroczono limit czasu wykonania.\n\n" +
                    "Spróbuj zmniejszyć liczbę zadań.");
        }

        int exitCode = process.exitValue();
        if (exitCode != 0) {
            throw new Exception("Uszkodzony plik wejściowy .json\n\n" +
                    "Plik harmonogramu zawiera nieprawidłowe dane.\n" +
                    "Upewnij się, że wybrany plik zawiera poprawny harmonogram.");
        }

        String updatedJson = Files.readString(schedulePath);
        for (String line : updatedJson.split("\n")) {
            if (line.contains("\"gant_diagram\"")) {
                String path = line.split(":")[1].trim()
                        .replace("\"", "")
                        .replace(",", "")
                        .trim();
                Path ganttPath = Paths.get(path);
                if (Files.exists(ganttPath)) {
                    return ganttPath;
                }
            }
        }

        throw new Exception("Uszkodzony plik wejściowy .json\n\n" +
                "Nie udało się wygenerować wykresu Gantta.\n" +
                "Sprawdź, czy plik zawiera prawidłowy harmonogram.");
    }

    /**
     * Czyści folder results przy zamknięciu aplikacji.
     *
     * Usuwa wszystkie pliki z katalogu results/, zachowując sam katalog.
     * Błędy są obsługiwane cicho, aby nie zakłócać procesu zamykania aplikacji.
     */
    public void cleanResultsFolder() {
        try {
            Path resultsPath = Paths.get(resultsDir);
            if (Files.exists(resultsPath) && Files.isDirectory(resultsPath)) {
                Files.walk(resultsPath)
                        .filter(Files::isRegularFile)
                        .forEach(file -> {
                            try {
                                Files.delete(file);
                            } catch (IOException e) {
                            }
                        });
            }
        } catch (IOException e) {
        }
    }
}
