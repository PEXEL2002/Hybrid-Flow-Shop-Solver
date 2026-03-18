package pl.pwr.inz.hfs.ui.view;

import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Parent;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.scene.layout.*;
import javafx.stage.FileChooser;
import javafx.stage.Stage;
import pl.pwr.inz.hfs.ui.model.ProblemInstance;
import pl.pwr.inz.hfs.ui.model.ScheduleResult;

import java.io.File;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

/**
 * Widok wyników optymalizacji z wizualizacją wykresu Gantta.
 *
 * Klasa odpowiada za prezentację wyników procesu optymalizacji harmonogramu produkcji.
 * Wyświetla wykres Gantta generowany przez algorytm optymalizacji oraz szczegółowe informacje
 * o rezultatach, takie jak wartość Cmax (całkowity czas zakończenia) i czas wykonania algorytmu.
 *
 * Widok zawiera panel nagłówkowy z logo PWR, centralną sekcję z wykresem Gantta i panelem
 * informacyjnym, oraz stopkę zawierającą dane autora i temat pracy. Użytkownik ma możliwość
 * eksportowania wykresu do pliku PNG, zapisywania harmonogramu w formacie JSON, zapisywania
 * instancji problemu lub powrotu do menu głównego celem rozwiązywania nowego problemu.
 */
public class ResultsView {

    private final Stage stage;
    private final BorderPane root;
    private final ScheduleResult result;
    private final String algorithm;
    private final ProblemInstance instance;

    /**
     * Konstruktor widoku wyników z domyślnym parametrem instancji (null).
     *
     * @param stage scena główna aplikacji
     * @param result rezultat optymalizacji
     * @param algorithm kod algorytmu użytego do optymalizacji
     */
    public ResultsView(Stage stage, ScheduleResult result, String algorithm) {
        this(stage, result, algorithm, null);
    }

    /**
     * Konstruktor widoku wyników optymalizacji.
     *
     * @param stage scena główna aplikacji
     * @param result rezultat optymalizacji
     * @param algorithm kod algorytmu użytego do optymalizacji
     * @param instance instancja problemu (może być null dla harmonogramów załadowanych z pliku)
     */
    public ResultsView(Stage stage, ScheduleResult result, String algorithm, ProblemInstance instance) {
        this.stage = stage;
        this.result = result;
        this.algorithm = algorithm;
        this.instance = instance;
        this.root = createLayout();
    }

    private BorderPane createLayout() {
        BorderPane layout = new BorderPane();
        layout.setPadding(new Insets(20));

        HBox header = createHeader();
        layout.setTop(header);

        HBox center = createCenterPanel();
        layout.setCenter(center);

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

        Label titleLabel = new Label("Wyniki Działania");
        titleLabel.getStyleClass().add("title-text");
        titleBox.getChildren().add(titleLabel);

        header.getChildren().addAll(logoBox, titleBox);
        return header;
    }

    private HBox createCenterPanel() {
        HBox center = new HBox(20);
        center.setAlignment(Pos.CENTER);
        center.setPadding(new Insets(20));

        VBox ganttBox = createGanttChartBox();
        VBox infoBox = createInfoBox();

        center.getChildren().addAll(ganttBox, infoBox);
        return center;
    }

    private VBox createGanttChartBox() {
        VBox box = new VBox(10);
        box.setAlignment(Pos.CENTER);
        box.setPrefWidth(600);

        Label chartLabel = new Label("Wykres Gantta");
        chartLabel.getStyleClass().add("section-title");

        ImageView ganttImageView = new ImageView();
        ganttImageView.setFitWidth(650);
        ganttImageView.setPreserveRatio(true);

        try {
            Path ganttPath = findGanttChart();
            if (ganttPath != null && Files.exists(ganttPath)) {
                Image ganttImage = new Image(ganttPath.toUri().toString());
                ganttImageView.setImage(ganttImage);
            } else {
                Label placeholderLabel = new Label("Wykres Gantta niedostępny\n(plik nie został wygenerowany)");
                placeholderLabel.getStyleClass().add("placeholder-text");
                placeholderLabel.setStyle("-fx-border-color: #ccc; -fx-border-width: 2; -fx-padding: 50;");
                placeholderLabel.setPrefSize(650, 350);
                placeholderLabel.setAlignment(Pos.CENTER);
                box.getChildren().addAll(chartLabel, placeholderLabel);
                return box;
            }
        } catch (Exception e) {
            System.err.println("Błąd wczytywania wykresu Gantta: " + e.getMessage());
        }

        box.getChildren().addAll(chartLabel, ganttImageView);
        return box;
    }

    private VBox createInfoBox() {
        VBox box = new VBox(15);
        box.setAlignment(Pos.TOP_CENTER);
        box.setPadding(new Insets(20));
        box.setPrefWidth(300);

        boolean isExistingSchedule = "existing".equalsIgnoreCase(algorithm);

        Label infoLabel = new Label("Wyniki Optymalizacji");
        infoLabel.getStyleClass().add("info-title");
        infoLabel.setWrapText(true);

        if (result.getAlgorithm() != null && !result.getAlgorithm().isEmpty()) {
            String algoText;
            if (isExistingSchedule) {
                algoText = "Wykorzystany algorytm do tworzenia harmonogramu: " + result.getAlgorithm();
            } else {
                algoText = "Algorytm: " + result.getAlgorithm();
            }
            Label algoLabel = new Label(algoText);
            algoLabel.getStyleClass().add("result-info");
            algoLabel.setWrapText(true);
            algoLabel.setMaxWidth(280);
            algoLabel.setAlignment(Pos.CENTER);
            algoLabel.setStyle("-fx-text-alignment: center;");
            box.getChildren().add(algoLabel);
        }

        Label cmaxLabel = new Label(String.format("Cmax: %.2f", result.getCmax()));
        cmaxLabel.getStyleClass().add("result-value");
        cmaxLabel.setStyle("-fx-font-size: 20px; -fx-font-weight: bold;");

        Label cmaxDescLabel = new Label("(Czas całkowitego zakończenia)");
        cmaxDescLabel.getStyleClass().add("help-text");
        cmaxDescLabel.setStyle("-fx-font-size: 11px; -fx-text-fill: #666;");

        Label timeLabel = null;
        if (!isExistingSchedule) {
            double timeValue = result.getTimeInMs();
            String timeText;

            System.out.println("DEBUG: Czas wykonania algorytmu (ms): " + timeValue);

            if (timeValue == 0.0) {
                timeText = "Czas wykonania: brak danych";
            } else if (timeValue < 1.0) {
                timeText = String.format("Czas wykonania algorytmu: %.0f μs", timeValue * 1000);
            } else if (timeValue < 1000) {
                timeText = String.format("Czas wykonania algorytmu: %.2f ms", timeValue);
            } else {
                timeText = String.format("Czas wykonania algorytmu: %.2f s", timeValue / 1000);
            }
            timeLabel = new Label(timeText);
            timeLabel.getStyleClass().add("result-info");
        }

        GridPane buttonsGrid = new GridPane();
        buttonsGrid.setAlignment(Pos.CENTER);
        buttonsGrid.setHgap(10);
        buttonsGrid.setVgap(10);
        buttonsGrid.setPadding(new Insets(20, 0, 0, 0));

        Button exportResultsBtn = new Button("Zapisz Wykres\nGantta do pliku");
        exportResultsBtn.getStyleClass().add("action-button");
        exportResultsBtn.setWrapText(true);
        exportResultsBtn.setPrefWidth(170);
        exportResultsBtn.setPrefHeight(75);
        exportResultsBtn.setStyle("-fx-font-size: 12px;");
        exportResultsBtn.setOnAction(e -> exportGanttChart());

        Button exportScheduleBtn = new Button("Zapisz\nHarmonogram\ndo JSON");
        exportScheduleBtn.getStyleClass().add("action-button");
        exportScheduleBtn.setWrapText(true);
        exportScheduleBtn.setPrefWidth(170);
        exportScheduleBtn.setPrefHeight(75);
        exportScheduleBtn.setStyle("-fx-font-size: 12px;");
        exportScheduleBtn.setOnAction(e -> exportSchedule());

        Button saveInstanceBtn = new Button("Zapisz\ninstancję\nproblemu");
        saveInstanceBtn.getStyleClass().add("action-button");
        saveInstanceBtn.setWrapText(true);
        saveInstanceBtn.setPrefWidth(170);
        saveInstanceBtn.setPrefHeight(75);
        saveInstanceBtn.setStyle("-fx-font-size: 12px;");
        saveInstanceBtn.setOnAction(e -> saveInstance());

        if (isExistingSchedule) {
            saveInstanceBtn.setDisable(true);
            saveInstanceBtn.setOpacity(0.5);
        }

        Button restartBtn = new Button("Zacznij\nod nowa\n(nowy problem)");
        restartBtn.getStyleClass().add("action-button");
        restartBtn.setWrapText(true);
        restartBtn.setPrefWidth(170);
        restartBtn.setPrefHeight(75);
        restartBtn.setStyle("-fx-font-size: 12px;");
        restartBtn.setOnAction(e -> restart());

        buttonsGrid.add(exportResultsBtn, 0, 0);
        buttonsGrid.add(exportScheduleBtn, 1, 0);
        buttonsGrid.add(saveInstanceBtn, 0, 1);
        buttonsGrid.add(restartBtn, 1, 1);

        if (result.getAlgorithm() == null || result.getAlgorithm().isEmpty()) {
            box.getChildren().add(infoLabel);
        }

        box.getChildren().add(cmaxLabel);
        box.getChildren().add(cmaxDescLabel);

        if (timeLabel != null) {
            box.getChildren().add(timeLabel);
        }

        box.getChildren().add(buttonsGrid);

        return box;
    }

    private HBox createFooter() {
        HBox footer = new HBox();
        footer.setAlignment(Pos.CENTER);
        footer.setPadding(new Insets(20));

        VBox footerContent = new VBox(5);
        footerContent.setAlignment(Pos.CENTER);

        Label authorLabel = new Label("Autor: Bartłomiej Adam Kuk");
        authorLabel.getStyleClass().add("footer-text");

        Label thesisLabel = new Label("Temat: Aplikacja wspomagająca harmonogramowanie produkcji dla wybranego zagadnienia szeregowania zadań");
        thesisLabel.getStyleClass().add("footer-text");
        thesisLabel.setWrapText(true);
        thesisLabel.setMaxWidth(800);
        thesisLabel.setAlignment(Pos.CENTER);

        footerContent.getChildren().addAll(authorLabel, thesisLabel);
        footer.getChildren().add(footerContent);
        return footer;
    }

    private Path findGanttChart() {
        if (result.getGantDiagram() != null && !result.getGantDiagram().isEmpty()) {
            Path ganttPath = Paths.get(result.getGantDiagram());
            if (Files.exists(ganttPath)) {
                System.out.println("Znaleziono wykres Gantta z JSON: " + ganttPath);
                return ganttPath;
            }
        }

        String[] possiblePaths = {
                "C:\\inz\\Python\\result_gantt.png",
                "../Python/result_gantt.png",
                "C:\\inz\\results\\" + algorithm + "_gantt.png",
                "../inz/results/" + algorithm + "_gantt.png",
                "./results/" + algorithm + "_gantt.png",
                "results/" + algorithm + "_gantt.png"
        };

        for (String pathStr : possiblePaths) {
            try {
                Path path = Paths.get(pathStr);
                if (Files.exists(path)) {
                    System.out.println("Znaleziono wykres Gantta: " + path);
                    return path;
                }
            } catch (Exception e) {
            }
        }

        System.out.println("Nie znaleziono wykresu Gantta");
        return null;
    }

    private void exportGanttChart() {
        FileChooser fileChooser = new FileChooser();
        fileChooser.setTitle("Zapisz wykres Gantta");
        fileChooser.setInitialFileName("gantt_chart_" + algorithm + ".png");
        fileChooser.getExtensionFilters().add(
                new FileChooser.ExtensionFilter("Obraz PNG", "*.png")
        );

        File file = fileChooser.showSaveDialog(stage);
        if (file != null) {
            try {
                Path ganttPath = findGanttChart();
                if (ganttPath != null) {
                    Files.copy(ganttPath, file.toPath());
                    showInfo("Wykres został zapisany pomyślnie");
                } else {
                    showError("Nie znaleziono wykresu Gantta");
                }
            } catch (Exception e) {
                showError("Błąd zapisu: " + e.getMessage());
            }
        }
    }

    private void exportSchedule() {
        FileChooser fileChooser = new FileChooser();
        fileChooser.setTitle("Zapisz harmonogram");
        fileChooser.setInitialFileName("schedule_" + algorithm + ".json");
        fileChooser.getExtensionFilters().add(
                new FileChooser.ExtensionFilter("Plik JSON", "*.json")
        );

        File file = fileChooser.showSaveDialog(stage);
        if (file != null) {
            try {
                String json = new com.google.gson.GsonBuilder()
                        .setPrettyPrinting()
                        .create()
                        .toJson(result);
                Files.writeString(file.toPath(), json);
                showInfo("Harmonogram został zapisany pomyślnie");
            } catch (Exception e) {
                showError("Błąd zapisu: " + e.getMessage());
            }
        }
    }

    private void saveInstance() {
        if (instance == null) {
            showError("Brak danych instancji problemu do zapisania");
            return;
        }

        FileChooser fileChooser = new FileChooser();
        fileChooser.setTitle("Zapisz instancję problemu");
        fileChooser.setInitialFileName("instance_" + System.currentTimeMillis() + ".json");
        fileChooser.getExtensionFilters().add(
                new FileChooser.ExtensionFilter("Plik JSON", "*.json")
        );

        File file = fileChooser.showSaveDialog(stage);
        if (file != null) {
            try {
                String json = instance.toJson();
                Files.writeString(file.toPath(), json);
                showInfo("Instancja problemu została zapisana pomyślnie");
            } catch (Exception e) {
                showError("Błąd zapisu instancji: " + e.getMessage());
            }
        }
    }

    private void restart() {
        MainMenuView mainMenuView = new MainMenuView(stage);
        stage.getScene().setRoot(mainMenuView.getRoot());
    }

    private void showInfo(String message) {
        javafx.scene.control.Alert alert = new javafx.scene.control.Alert(
                javafx.scene.control.Alert.AlertType.INFORMATION
        );
        alert.setTitle("Informacja");
        alert.setHeaderText(null);
        alert.setContentText(message);
        alert.showAndWait();
    }

    private void showError(String message) {
        javafx.scene.control.Alert alert = new javafx.scene.control.Alert(
                javafx.scene.control.Alert.AlertType.ERROR
        );
        alert.setTitle("Błąd");
        alert.setHeaderText("Wystąpił błąd");
        alert.setContentText(message);
        alert.showAndWait();
    }

    /**
     * Zwraca element główny (root) widoku.
     *
     * @return element BorderPane zawierający interfejs użytkownika widoku wyników
     */
    public Parent getRoot() {
        return root;
    }
}
