package pl.pwr.inz.hfs.ui.view;

import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Parent;
import javafx.scene.control.*;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.scene.layout.*;
import javafx.stage.FileChooser;
import javafx.stage.Stage;
import pl.pwr.inz.hfs.ui.model.ProblemInstance;

import java.io.File;
import java.io.InputStream;
import java.nio.file.Files;
import java.util.Random;

/**
 * Widok wprowadzania danych instancji problemu.
 *
 * Umożliwia użytkownikowi zdefiniowanie parametrów problemu HFS-SDST:
 * liczba zadań, etapów, maszyn, współczynnik uczenia, czasy przetwarzania
 * i przezbrojeń. Obsługuje zarówno wprowadzanie ręczne jak i import z pliku JSON.
 */
public class DataInputView {

    private final Stage stage;
    private final BorderPane root;
    private final String selectedAlgorithm;
    private final boolean generateRandom;

    private TextField numJobsField;
    private TextField numStagesField;
    private VBox machinesInputBox;
    private TextField learningCoeffField;
    private TextField learningStagesField;
    private TextArea processingTimesField;
    private TextArea setupTimesField;

    private TextField minProcessingTimeField;
    private TextField maxProcessingTimeField;
    private TextField minSetupTimeField;
    private TextField maxSetupTimeField;

    private java.util.List<TextField> machineFields = new java.util.ArrayList<>();

    /**
     * Konstruktor widoku wprowadzania danych.
     *
     * @param stage Główne okno aplikacji
     * @param selectedAlgorithm Wybrany algorytm (może być null)
     * @param generateRandom Czy generować losowe dane testowe
     */
    public DataInputView(Stage stage, String selectedAlgorithm, boolean generateRandom) {
        this.stage = stage;
        this.selectedAlgorithm = selectedAlgorithm;
        this.generateRandom = generateRandom;
        this.root = createLayout();
    }

    private BorderPane createLayout() {
        BorderPane layout = new BorderPane();
        layout.setPadding(new Insets(20));

        HBox header = createHeader();
        layout.setTop(header);

        VBox center = createCenterPanel();

        HBox centerWrapper = new HBox();
        centerWrapper.setAlignment(Pos.CENTER);
        centerWrapper.getChildren().add(center);

        ScrollPane scrollPane = new ScrollPane(centerWrapper);
        scrollPane.setFitToWidth(true);
        scrollPane.setStyle("-fx-background-color: transparent;");
        layout.setCenter(scrollPane);

        HBox footer = createFooter();
        layout.setBottom(footer);

        return layout;
    }

    private HBox createHeader() {
        HBox header = new HBox(20);
        header.setAlignment(Pos.CENTER_LEFT);
        header.setPadding(new Insets(10, 20, 10, 20));

        HBox logoBox = new HBox();
        logoBox.setAlignment(Pos.CENTER_LEFT);

        try {
            InputStream logoStream = getClass().getResourceAsStream("/images/pwr_logo.png");
            if (logoStream != null) {
                Image logoImage = new Image(logoStream);
                ImageView logoView = new ImageView(logoImage);
                logoView.setFitHeight(60);
                logoView.setPreserveRatio(true);
                logoBox.getChildren().add(logoView);
            } else {
                Label logoLabel = new Label("PWR");
                logoLabel.getStyleClass().add("logo-text");
                logoBox.getChildren().add(logoLabel);
            }
        } catch (Exception e) {
            Label logoLabel = new Label("PWR");
            logoLabel.getStyleClass().add("logo-text");
            logoBox.getChildren().add(logoLabel);
        }

        VBox titleBox = new VBox(5);
        titleBox.setAlignment(Pos.CENTER);
        HBox.setHgrow(titleBox, javafx.scene.layout.Priority.ALWAYS);

        Label titleLabel = new Label("Wprowadź Dane");
        titleLabel.getStyleClass().add("title-text");
        titleBox.getChildren().add(titleLabel);

        header.getChildren().addAll(logoBox, titleBox);
        return header;
    }

    private VBox createCenterPanel() {
        VBox center = new VBox(15);
        center.setAlignment(Pos.CENTER);
        center.setPadding(new Insets(20));
        center.setMaxWidth(900);

        Label instructionLabel = new Label("Co wprowadzamy:");
        instructionLabel.getStyleClass().add("section-title");

        HBox inputMethodBox = new HBox(20);
        inputMethodBox.setAlignment(Pos.CENTER);

        Button loadFileButton = new Button("Wczytaj z pliku JSON");
        loadFileButton.getStyleClass().add("secondary-button");
        loadFileButton.setOnAction(e -> loadFromFile());

        Label orLabel = new Label("LUB wprowadź ręcznie:");

        inputMethodBox.getChildren().addAll(loadFileButton, orLabel);

        HBox formContainer = createFormContainer();
        VBox optionalFields = createOptionalFieldsSection();

        center.getChildren().addAll(instructionLabel, inputMethodBox, formContainer, optionalFields);
        return center;
    }

    private HBox createFormContainer() {
        HBox container = new HBox(30);
        container.setAlignment(Pos.CENTER);
        container.setPadding(new Insets(30, 20, 20, 20));

        VBox leftColumn = createLeftColumn();
        VBox rightColumn = createRightColumn();

        container.getChildren().addAll(leftColumn, rightColumn);
        return container;
    }

    private VBox createLeftColumn() {
        VBox column = new VBox(15);
        column.setPrefWidth(400);
        column.setAlignment(Pos.TOP_CENTER); // Wyśrodkowanie zawartości
        column.setStyle("-fx-border-color: #ddd; -fx-border-radius: 5; -fx-padding: 15; -fx-background-color: white; -fx-background-radius: 5;");

        Label titleLabel = new Label("Parametry podstawowe");
        titleLabel.setStyle("-fx-font-size: 14px; -fx-font-weight: bold; -fx-text-fill: #2196F3;");

        GridPane grid = createBasicParamsGrid();

        column.getChildren().addAll(titleLabel, grid);
        return column;
    }

    private GridPane createBasicParamsGrid() {
        GridPane grid = new GridPane();
        grid.setHgap(10);
        grid.setVgap(12);

        int row = 0;

        Label jobsLabel = new Label("Liczba zadań (n):");
        grid.add(jobsLabel, 0, row);
        numJobsField = new TextField("3");
        numJobsField.setPromptText("max. 50");
        grid.add(numJobsField, 1, row++);
        Label jobsHelp = new Label("(maksymalnie 50)");
        jobsHelp.setStyle("-fx-font-size: 9px; -fx-text-fill: #999;");
        grid.add(jobsHelp, 1, row++);

        Label stagesLabel = new Label("Liczba etapów (s):");
        grid.add(stagesLabel, 0, row);
        numStagesField = new TextField("2");
        numStagesField.setPromptText("max. 20");
        numStagesField.textProperty().addListener((obs, oldVal, newVal) -> {
            if (newVal != null && !newVal.equals(oldVal)) {
                updateMachineFields();
                updateLearningStagesField();
            }
        });
        grid.add(numStagesField, 1, row++);
        Label stagesHelp = new Label("(maksymalnie 20)");
        stagesHelp.setStyle("-fx-font-size: 9px; -fx-text-fill: #999;");
        grid.add(stagesHelp, 1, row++);

        grid.add(new Label("Współczynnik uczenia (α):"), 0, row);
        learningCoeffField = new TextField("0.15");
        learningCoeffField.setPromptText("np. 0.15");
        grid.add(learningCoeffField, 1, row++);

        grid.add(new Label("Etapy uczące się:"), 0, row);
        learningStagesField = new TextField("10");
        learningStagesField.setPromptText("np. 101");
        grid.add(learningStagesField, 1, row++);

        Label learningHelp = new Label("(ciąg binarny, 1=uczący się, długość = liczbie etapów)");
        learningHelp.getStyleClass().add("help-text");
        learningHelp.setStyle("-fx-font-size: 10px;");
        grid.add(learningHelp, 0, row++, 2, 1);

        return grid;
    }

    private VBox createRightColumn() {
        VBox column = new VBox(10);
        column.setPrefWidth(400);
        column.setAlignment(Pos.TOP_CENTER); // Wyśrodkowanie zawartości
        column.setStyle("-fx-border-color: #ddd; -fx-border-radius: 5; -fx-padding: 15; -fx-background-color: white; -fx-background-radius: 5;");

        Label titleLabel = new Label("--- Liczba maszyn na każdym etapie ---");
        titleLabel.setStyle("-fx-font-size: 14px; -fx-font-weight: bold; -fx-text-fill: #2196F3;");

        machinesInputBox = new VBox(10);
        machinesInputBox.setPadding(new Insets(10));
        machinesInputBox.setAlignment(Pos.CENTER); // Wyśrodkowanie pól maszyn

        updateMachineFields();

        column.getChildren().addAll(titleLabel, machinesInputBox);
        return column;
    }
    private VBox createOptionalFieldsSection() {
        VBox optionalSection = new VBox(15);
        optionalSection.setPadding(new Insets(20, 0, 0, 0));
        optionalSection.setAlignment(Pos.CENTER);

        Label optionalLabel = new Label("--- Opcjonalnie (zostaw puste dla losowych) ---");
        optionalLabel.getStyleClass().add("section-title");
        optionalLabel.setStyle("-fx-font-size: 14px; -fx-text-fill: #666; -fx-font-weight: bold;");

        HBox rangesBox = new HBox(30);
        rangesBox.setAlignment(Pos.CENTER);
        rangesBox.setPadding(new Insets(10));

        VBox procRangeBox = new VBox(10);
        procRangeBox.setAlignment(Pos.CENTER);
        procRangeBox.setStyle("-fx-border-color: #ddd; -fx-border-radius: 5; -fx-padding: 15; -fx-background-color: #f9f9f9; -fx-background-radius: 5;");
        procRangeBox.setPrefWidth(350);
        Label procRangeLabel = new Label("Zakres losowania czasów wykonania");
        procRangeLabel.setStyle("-fx-font-weight: bold; -fx-font-size: 12px;");

        HBox minProcBox = new HBox(10);
        minProcBox.setAlignment(Pos.CENTER);
        minProcBox.getChildren().addAll(new Label("Min:"), minProcessingTimeField = new TextField("1"));
        minProcessingTimeField.setPrefWidth(80);

        HBox maxProcBox = new HBox(10);
        maxProcBox.setAlignment(Pos.CENTER);
        maxProcBox.getChildren().addAll(new Label("Max:"), maxProcessingTimeField = new TextField("20"));
        maxProcessingTimeField.setPrefWidth(80);

        Label procRangeHelp = new Label("(zakres dla generowania losowych czasów)");
        procRangeHelp.setStyle("-fx-font-size: 10px; -fx-text-fill: #666;");
        procRangeBox.getChildren().addAll(procRangeLabel, minProcBox, maxProcBox, procRangeHelp);

        VBox setupRangeBox = new VBox(10);
        setupRangeBox.setAlignment(Pos.CENTER);
        setupRangeBox.setStyle("-fx-border-color: #ddd; -fx-border-radius: 5; -fx-padding: 15; -fx-background-color: #f9f9f9; -fx-background-radius: 5;");
        setupRangeBox.setPrefWidth(350);
        Label setupRangeLabel = new Label("Zakres losowania czasów przezbrojeń");
        setupRangeLabel.setStyle("-fx-font-weight: bold; -fx-font-size: 12px;");

        HBox minSetupBox = new HBox(10);
        minSetupBox.setAlignment(Pos.CENTER);
        minSetupBox.getChildren().addAll(new Label("Min:"), minSetupTimeField = new TextField("0"));
        minSetupTimeField.setPrefWidth(80);

        HBox maxSetupBox = new HBox(10);
        maxSetupBox.setAlignment(Pos.CENTER);
        maxSetupBox.getChildren().addAll(new Label("Max:"), maxSetupTimeField = new TextField("10"));
        maxSetupTimeField.setPrefWidth(80);

        Label setupRangeHelp = new Label("(zakres dla generowania losowych przezbrojeń)");
        setupRangeHelp.setStyle("-fx-font-size: 10px; -fx-text-fill: #666;");
        setupRangeBox.getChildren().addAll(setupRangeLabel, minSetupBox, maxSetupBox, setupRangeHelp);

        rangesBox.getChildren().addAll(procRangeBox, setupRangeBox);

        VBox procBox = new VBox(5);
        procBox.setAlignment(Pos.CENTER);
        Label procLabel = new Label("Lub wprowadź czasy wykonania ręcznie:");
        procLabel.setStyle("-fx-font-weight: bold;");
        processingTimesField = new TextArea();
        processingTimesField.setPromptText("Format: Enter rozdziela zadania, średniki rozdzielają etapy, przecinki rozdzielają maszyny. Przykład (2 zadania, 3 etapy, maszyny [1,2,2]): Zadanie 1: 8; 2, 4; 4, 1  |  Zadanie 2: 4; 4, 4; 1, 2");
        processingTimesField.setPrefRowCount(4);
        processingTimesField.setPrefColumnCount(50);
        processingTimesField.setMaxWidth(800);
        Label procHelp = new Label("Enter rozdziela zadania, średniki rozdzielają etapy, przecinki rozdzielają maszyny. Jeśli puste, czasy będą losowane.");
        procHelp.setStyle("-fx-font-size: 10px; -fx-text-fill: #666;");
        procBox.getChildren().addAll(procLabel, processingTimesField, procHelp);

        VBox setupBox = new VBox(5);
        setupBox.setAlignment(Pos.CENTER);
        Label setupLabel = new Label("Lub wprowadź czasy przezbrojeń ręcznie:");
        setupLabel.setStyle("-fx-font-weight: bold;");
        setupTimesField = new TextArea();
        setupTimesField.setPromptText("Format: Enter rozdziela pary zadań (i->j), średniki rozdzielają etapy, przecinki rozdzielają maszyny. Przykład (2 zadania, 3 etapy, maszyny [1,2,2]): Para 0->0: 0; 0, 0; 0, 0  |  Para 0->1: 1; 2, 3; 4, 5  |  Para 1->0: 2; 1, 2; 3, 4  |  Para 1->1: 3; 4, 5; 6, 7");
        setupTimesField.setPrefRowCount(6);
        setupTimesField.setPrefColumnCount(50);
        setupTimesField.setMaxWidth(800);
        Label setupHelp = new Label("Enter rozdziela pary zadań, średniki rozdzielają etapy, przecinki rozdzielają maszyny. Jeśli puste, czasy będą losowane.");
        setupHelp.setStyle("-fx-font-size: 10px; -fx-text-fill: #666;");
        setupBox.getChildren().addAll(setupLabel, setupTimesField, setupHelp);

        optionalSection.getChildren().addAll(optionalLabel, rangesBox, procBox, setupBox);
        return optionalSection;
    }

    private HBox createFooter() {
        HBox footer = new HBox(20);
        footer.setAlignment(Pos.CENTER);
        footer.setPadding(new Insets(20));

        Button backButton = new Button("← Wstecz");
        backButton.getStyleClass().add("back-button");
        backButton.setOnAction(e -> goBack());

        VBox footerContent = new VBox(5);
        footerContent.setAlignment(Pos.CENTER);

        Label authorLabel = new Label("Autor: Bartłomiej Adam Kuk");
        authorLabel.getStyleClass().add("footer-text");

        Label thesisLabel = new Label("Temat: Aplikacja wspomagająca harmonogramowanie produkcji dla wybranego zagadnienia szeregowania zadań");
        thesisLabel.getStyleClass().add("footer-text");
        thesisLabel.setWrapText(true);
        thesisLabel.setMaxWidth(500);
        thesisLabel.setAlignment(Pos.CENTER);

        footerContent.getChildren().addAll(authorLabel, thesisLabel);

        Button nextButton = new Button("Dalej →");
        nextButton.getStyleClass().add("primary-button");
        nextButton.setOnAction(e -> handleNext());

        footer.getChildren().addAll(backButton, footerContent, nextButton);
        return footer;
    }

    /**
     * Aktualizuje pola wprowadzania liczby maszyn dla każdego etapu
     */
    private void updateMachineFields() {
        try {
            int numStages = Integer.parseInt(numStagesField.getText().trim());
            if (numStages <= 0 || numStages > 10) {
                return; // Ignoruj nieprawidłowe wartości
            }

            machinesInputBox.getChildren().clear();
            machineFields.clear();

            for (int i = 0; i < numStages; i++) {
                HBox stageBox = new HBox(10);
                stageBox.setAlignment(Pos.CENTER_LEFT);

                Label stageLabel = new Label("Etap " + (i + 1) + ":");
                stageLabel.setMinWidth(80);
                stageLabel.setStyle("-fx-font-weight: bold;");

                // Ustaw domyślne wartości: etap 1 = 1 maszyna, etap 2 = 2 maszyny, reszta = 1
                String defaultValue = (i == 1) ? "2" : "1";
                TextField machineField = new TextField(defaultValue);
                machineField.setPromptText("Liczba maszyn");
                machineField.setPrefWidth(150);
                machineFields.add(machineField);

                Label helpLabel = new Label("(liczba maszyn na tym etapie)");
                helpLabel.setStyle("-fx-text-fill: #666; -fx-font-size: 10px;");

                stageBox.getChildren().addAll(stageLabel, machineField, helpLabel);
                machinesInputBox.getChildren().add(stageBox);
            }

            // Ustaw domyślne wartości jeśli tryb losowy
            if (generateRandom && numStages <= machineFields.size()) {
                for (int i = 0; i < numStages; i++) {
                    machineFields.get(i).setText(String.valueOf(1 + (i % 2)));
                }
            }

        } catch (NumberFormatException e) {
            // Ignoruj błędy parsowania podczas wpisywania
        }
    }

    /**
     * Aktualizuje pole learning stages aby miało odpowiednią długość
     */
    private void updateLearningStagesField() {
        try {
            int stages = Integer.parseInt(numStagesField.getText().trim());
            if (stages > 0 && stages <= 10) {
                StringBuilder sb = new StringBuilder();
                for (int i = 0; i < stages; i++) {
                    sb.append("1");
                }
                learningStagesField.setText(sb.toString());
            }
        } catch (NumberFormatException e) {
            // Ignoruj podczas wpisywania
        }
    }

    private void loadFromFile() {
        FileChooser fileChooser = new FileChooser();
        fileChooser.setTitle("Wybierz plik JSON");
        fileChooser.getExtensionFilters().add(
                new FileChooser.ExtensionFilter("Pliki JSON", "*.json")
        );

        File file = fileChooser.showOpenDialog(stage);
        if (file != null) {
            try {
                String json = Files.readString(file.toPath());
                ProblemInstance instance = ProblemInstance.fromJson(json);

                // Ustaw algorytm jeśli został wybrany
                if (selectedAlgorithm != null) {
                    instance.setAlgorithm(selectedAlgorithm);
                }

                // Przejdź do optymalizacji
                OptimizationProgressView progressView = new OptimizationProgressView(stage, instance);
                stage.getScene().setRoot(progressView.getRoot());

            } catch (Exception ex) {
                showError("Błąd wczytywania pliku: " + ex.getMessage());
            }
        }
    }

    private void handleNext() {
        try {
            // Walidacja i parsowanie danych
            int numJobs = Integer.parseInt(numJobsField.getText().trim());
            int numStages = Integer.parseInt(numStagesField.getText().trim());
            double learningCoeff = Double.parseDouble(learningCoeffField.getText().trim());
            String learningStages = learningStagesField.getText().trim();

            // Ograniczenia podstawowe
            if (numJobs <= 0 || numStages <= 0) {
                showError("Liczba zadań i etapów musi być większa od 0");
                return;
            }

            if (numJobs > 50) {
                showError("Liczba zadań nie może przekraczać 50");
                return;
            }

            if (numStages > 20) {
                showError("Liczba etapów nie może przekraczać 20");
                return;
            }

            // Pobierz liczbę maszyn z dynamicznych pól
            if (machineFields.size() != numStages) {
                showError("Liczba pól maszyn nie odpowiada liczbie etapów. Sprawdź pole 'Liczba etapów'.");
                return;
            }

            int[] machinesPerStage = new int[numStages];
            for (int i = 0; i < numStages; i++) {
                try {
                    machinesPerStage[i] = Integer.parseInt(machineFields.get(i).getText().trim());
                    if (machinesPerStage[i] <= 0) {
                        showError("Liczba maszyn na etapie " + (i + 1) + " musi być większa od 0");
                        return;
                    }
                } catch (NumberFormatException e) {
                    showError("Nieprawidłowa liczba maszyn na etapie " + (i + 1));
                    return;
                }
            }

            // Walidacja: przynajmniej jeden etap musi mieć >= 2 maszyny
            boolean hasMultipleMachines = false;
            for (int machines : machinesPerStage) {
                if (machines >= 2) {
                    hasMultipleMachines = true;
                    break;
                }
            }
            if (!hasMultipleMachines) {
                showError("Przynajmniej jeden etap musi mieć 2 lub więcej maszyn.\n" +
                         "Problem HFS wymaga równoległych maszyn na co najmniej jednym etapie.");
                return;
            }

            if (learningStages.length() != numStages) {
                showError("Długość ciągu etapów uczących się musi odpowiadać liczbie etapów");
                return;
            }

            if (learningCoeff < 0 || learningCoeff > 1) {
                showError("Współczynnik uczenia musi być z przedziału [0, 1]");
                return;
            }

            // Utworzenie instancji
            String algorithm = selectedAlgorithm != null ? selectedAlgorithm : "greedy";
            ProblemInstance instance = new ProblemInstance(
                    algorithm, numStages, numJobs, machinesPerStage,
                    learningCoeff, learningStages
            );

            // Parsowanie opcjonalnych czasów wykonania
            String procTimesText = processingTimesField.getText().trim();
            if (!procTimesText.isEmpty()) {
                parseProcessingTimes(instance, procTimesText);
            } else if (generateRandom) {
                generateRandomTimes(instance);
            } else {
                // Jeśli nie podano i nie jest losowe, wygeneruj losowe
                generateRandomTimes(instance);
            }

            // Parsowanie opcjonalnych czasów przezbrojeń
            String setupTimesText = setupTimesField.getText().trim();
            if (!setupTimesText.isEmpty()) {
                parseSetupTimes(instance, setupTimesText);
            } else if (instance.getSetupTimes() == null) {
                // Wygeneruj losowe czasy przezbrojeń jeśli nie podano
                generateRandomSetupTimes(instance);
            }

            // Przejście do wyboru algorytmu
            AlgorithmSelectionView algorithmView = new AlgorithmSelectionView(stage, instance);
            stage.getScene().setRoot(algorithmView.getRoot());

        } catch (NumberFormatException ex) {
            showError("Nieprawidłowy format liczby: " + ex.getMessage());
        } catch (Exception ex) {
            showError("Błąd: " + ex.getMessage());
        }
    }

    private void generateRandomTimes(ProblemInstance instance) {
        Random rand = new Random();
        int numJobs = instance.getNumJobs();
        int numStages = instance.getNumStages();
        int[] machinesPerStage = instance.getMachinesPerStage();

        // Pobierz zakresy z pól (lub użyj domyślnych wartości)
        int minProc = 1, maxProc = 20;
        int minSetup = 0, maxSetup = 10;

        try {
            minProc = Integer.parseInt(minProcessingTimeField.getText().trim());
            maxProc = Integer.parseInt(maxProcessingTimeField.getText().trim());
        } catch (Exception e) {
            // Użyj domyślnych wartości
        }

        try {
            minSetup = Integer.parseInt(minSetupTimeField.getText().trim());
            maxSetup = Integer.parseInt(maxSetupTimeField.getText().trim());
        } catch (Exception e) {
            // Użyj domyślnych wartości
        }

        // Walidacja zakresów
        if (minProc >= maxProc) {
            maxProc = minProc + 1;
        }
        if (minSetup >= maxSetup) {
            maxSetup = minSetup + 1;
        }

        // Generowanie czasów operacji z podanego zakresu
        double[][][] processingTimes = instance.getProcessingTimes();
        for (int j = 0; j < numJobs; j++) {
            for (int s = 0; s < numStages; s++) {
                for (int m = 0; m < machinesPerStage[s]; m++) {
                    processingTimes[j][s][m] = minProc + rand.nextInt(maxProc - minProc + 1);
                }
            }
        }

        // Generowanie czasów przezbrojeń z podanego zakresu
        double[][][][] setupTimes = instance.getSetupTimes();
        for (int i = 0; i < numJobs; i++) {
            for (int j = 0; j < numJobs; j++) {
                for (int s = 0; s < numStages; s++) {
                    for (int m = 0; m < machinesPerStage[s]; m++) {
                        setupTimes[i][j][s][m] = minSetup + rand.nextInt(maxSetup - minSetup + 1);
                    }
                }
            }
        }
    }

    private void parseProcessingTimes(ProblemInstance instance, String text) throws Exception {
        // Format: Enter rozdziela zadania, średniki rozdzielają etapy, przecinki rozdzielają maszyny
        // Przykład: 8; 2, 4; 4, 1
        //           4; 4, 4; 1, 2

        String[] lines = text.trim().split("\n");
        int numJobs = instance.getNumJobs();
        int numStages = instance.getNumStages();
        int[] machinesPerStage = instance.getMachinesPerStage();

        if (lines.length != numJobs) {
            throw new Exception("Liczba wierszy (zadań) musi być równa " + numJobs + ", ale jest " + lines.length);
        }

        double[][][] processingTimes = instance.getProcessingTimes();

        for (int j = 0; j < numJobs; j++) {
            String[] stages = lines[j].trim().split(";");
            if (stages.length != numStages) {
                throw new Exception("Zadanie " + (j+1) + ": liczba etapów musi być równa " + numStages + ", ale jest " + stages.length);
            }

            for (int s = 0; s < numStages; s++) {
                String[] machines = stages[s].trim().split(",");

                // Jeśli jest tylko jedna wartość dla wszystkich maszyn
                if (machines.length == 1) {
                    double time = Double.parseDouble(machines[0].trim());
                    for (int m = 0; m < machinesPerStage[s]; m++) {
                        processingTimes[j][s][m] = time;
                    }
                } else if (machines.length == machinesPerStage[s]) {
                    // Jeśli są osobne wartości dla każdej maszyny
                    for (int m = 0; m < machinesPerStage[s]; m++) {
                        processingTimes[j][s][m] = Double.parseDouble(machines[m].trim());
                    }
                } else {
                    throw new Exception("Zadanie " + (j+1) + ", etap " + (s+1) + ": liczba maszyn musi być 1 lub " + machinesPerStage[s] + ", ale jest " + machines.length);
                }
            }
        }
    }

    private void parseSetupTimes(ProblemInstance instance, String text) throws Exception {
        // Format: Enter rozdziela pary zadań (i->j), średniki rozdzielają etapy, przecinki rozdzielają maszyny
        // Przykład dla 2 zadań, 3 etapów, maszyny [1,2,2]:
        // 0; 0, 0; 0, 0
        // 1; 2, 3; 4, 5
        // 2; 1, 2; 3, 4
        // 3; 4, 5; 6, 7

        String[] lines = text.trim().split("\n");
        int numJobs = instance.getNumJobs();
        int numStages = instance.getNumStages();
        int[] machinesPerStage = instance.getMachinesPerStage();

        // Oczekiwana liczba linii: numJobs * numJobs (macierz przezbrojeń)
        int expectedLines = numJobs * numJobs;
        if (lines.length != expectedLines) {
            throw new Exception("Liczba wierszy musi być równa " + expectedLines + " (liczba zadań × liczba zadań), ale jest " + lines.length);
        }

        double[][][][] setupTimes = instance.getSetupTimes();

        int lineIndex = 0;
        for (int i = 0; i < numJobs; i++) {
            for (int j = 0; j < numJobs; j++) {
                String line = lines[lineIndex].trim();
                String[] stages = line.split(";");

                if (stages.length != numStages) {
                    throw new Exception("Wiersz " + (lineIndex+1) + " (przezbrojenie " + i + "->" + j + "): liczba etapów musi być równa " + numStages + ", ale jest " + stages.length);
                }

                for (int s = 0; s < numStages; s++) {
                    String[] machines = stages[s].trim().split(",");

                    // Jeśli jest tylko jedna wartość dla wszystkich maszyn
                    if (machines.length == 1) {
                        double time = Double.parseDouble(machines[0].trim());
                        for (int m = 0; m < machinesPerStage[s]; m++) {
                            setupTimes[i][j][s][m] = time;
                        }
                    } else if (machines.length == machinesPerStage[s]) {
                        // Jeśli są osobne wartości dla każdej maszyny
                        for (int m = 0; m < machinesPerStage[s]; m++) {
                            setupTimes[i][j][s][m] = Double.parseDouble(machines[m].trim());
                        }
                    } else {
                        throw new Exception("Wiersz " + (lineIndex+1) + " (przezbrojenie " + i + "->" + j + "), etap " + (s+1) + ": liczba maszyn musi być 1 lub " + machinesPerStage[s] + ", ale jest " + machines.length);
                    }
                }

                lineIndex++;
            }
        }
    }

    private void generateRandomSetupTimes(ProblemInstance instance) {
        Random rand = new Random();
        int numJobs = instance.getNumJobs();
        int numStages = instance.getNumStages();
        int[] machinesPerStage = instance.getMachinesPerStage();

        double[][][][] setupTimes = instance.getSetupTimes();
        for (int i = 0; i < numJobs; i++) {
            for (int j = 0; j < numJobs; j++) {
                for (int s = 0; s < numStages; s++) {
                    for (int m = 0; m < machinesPerStage[s]; m++) {
                        setupTimes[i][j][s][m] = 1 + rand.nextInt(10);
                    }
                }
            }
        }
    }

    private void goBack() {
        if (selectedAlgorithm != null) {
            AlgorithmSelectionView view = new AlgorithmSelectionView(stage);
            stage.getScene().setRoot(view.getRoot());
        } else {
            MainMenuView view = new MainMenuView(stage);
            stage.getScene().setRoot(view.getRoot());
        }
    }

    private void showError(String message) {
        Alert alert = new Alert(Alert.AlertType.ERROR);
        alert.setTitle("Błąd");
        alert.setHeaderText("Nieprawidłowe dane");
        alert.setContentText(message);
        alert.showAndWait();
    }

    /**
     * Zwraca główny kontener widoku.
     *
     * @return Kontener BorderPane z kompletnym układem widoku wprowadzania danych
     */
    public Parent getRoot() {
        return root;
    }
}
