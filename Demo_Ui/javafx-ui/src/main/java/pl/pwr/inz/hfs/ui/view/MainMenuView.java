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
import pl.pwr.inz.hfs.ui.service.PythonService;

import java.io.File;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

/**
 * Widok głównego menu aplikacji.
 *
 * Prezentuje trzy główne opcje użytkownika:
 * - Załadowanie instancji problemu z pliku JSON
 * - Wygenerowanie wykresu Gantta z istniejącego harmonogramu
 * - Utworzenie nowego harmonogramu (wprowadzanie danych i wybór algorytmu)
 */
public class MainMenuView {

    private final Stage stage;
    private final BorderPane root;

    /**
     * Konstruktor widoku głównego menu.
     *
     * @param stage Główne okno aplikacji
     */
    public MainMenuView(Stage stage) {
        this.stage = stage;
        this.root = createLayout();
    }

    private BorderPane createLayout() {
        BorderPane layout = new BorderPane();
        layout.setPadding(new Insets(20));

        HBox header = createHeader();
        layout.setTop(header);

        VBox center = createCenterPanel();
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

        Label titleLabel = new Label("Wybierz Akcje");
        titleLabel.getStyleClass().add("title-text");
        titleBox.getChildren().add(titleLabel);

        header.getChildren().addAll(logoBox, titleBox);
        return header;
    }

    private VBox createCenterPanel() {
        VBox center = new VBox(20);
        center.setAlignment(Pos.CENTER);
        center.setPadding(new Insets(40));

        HBox buttonsRow = new HBox(30);
        buttonsRow.setAlignment(Pos.CENTER);

        Button loadFromFileBtn = createMenuButton(
                "Załaduj instancję z pliku",
                "Wczytaj instancję problemu z istniejącego pliku JSON"
        );
        loadFromFileBtn.setOnAction(e -> handleLoadFromFile());

        Button generateGanttBtn = createMenuButton(
                "Wygeneruj wykres Gantta\nz istniejącego harmonogramu",
                "Wizualizuj gotowy harmonogram"
        );
        generateGanttBtn.setOnAction(e -> handleGenerateGantt());

        Button createScheduleBtn = createMenuButton(
                "Tworzenie lub generowanie\nharmonogramu",
                "Wprowadź dane i uruchom algorytm optymalizacji"
        );
        createScheduleBtn.setOnAction(e -> handleCreateSchedule());

        buttonsRow.getChildren().addAll(loadFromFileBtn, generateGanttBtn, createScheduleBtn);

        center.getChildren().add(buttonsRow);
        return center;
    }

    private Button createMenuButton(String title, String description) {
        VBox buttonContent = new VBox(5);
        buttonContent.setAlignment(Pos.CENTER);

        Label titleLabel = new Label(title);
        titleLabel.getStyleClass().add("button-title");
        titleLabel.setWrapText(true);
        titleLabel.setMaxWidth(280);
        titleLabel.setAlignment(Pos.CENTER);
        titleLabel.setStyle("-fx-text-alignment: center;");

        Label descLabel = new Label(description);
        descLabel.getStyleClass().add("button-description");
        descLabel.setWrapText(true);
        descLabel.setMaxWidth(280);
        descLabel.setAlignment(Pos.CENTER);
        descLabel.setStyle("-fx-text-alignment: center;");

        buttonContent.getChildren().addAll(titleLabel, descLabel);

        Button button = new Button();
        button.setGraphic(buttonContent);
        button.getStyleClass().add("menu-button");
        button.setPrefWidth(300);
        button.setPrefHeight(120);

        return button;
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

    /**
     * Obsługuje ładowanie instancji problemu z pliku JSON.
     *
     * Rozróżnia pliki z danymi wejściowymi (instancja problemu)
     * oraz plikami wynikowymi (harmonogram).
     */
    private void handleLoadFromFile() {
        FileChooser fileChooser = new FileChooser();
        fileChooser.setTitle("Wybierz plik JSON z danymi");
        fileChooser.getExtensionFilters().add(
                new FileChooser.ExtensionFilter("Pliki JSON", "*.json")
        );

        File file = fileChooser.showOpenDialog(stage);
        if (file != null) {
            try {
                String json = Files.readString(file.toPath());

                if (json.contains("\"algorithm\"")) {
                    ProblemInstance instance = ProblemInstance.fromJson(json);
                    showAlgorithmSelection(instance);
                } else if (json.contains("\"schedule\"")) {
                    ScheduleResult result = ScheduleResult.fromJson(json);
                    showResults(result, "unknown");
                } else {
                    showError("Nieprawidłowy format pliku JSON");
                }
            } catch (Exception ex) {
                showError("Błąd wczytywania pliku: " + ex.getMessage());
            }
        }
    }

    /**
     * Obsługuje tworzenie nowego harmonogramu.
     *
     * Przekierowuje do widoku wprowadzania danych.
     */
    private void handleCreateSchedule() {
        DataInputView dataInputView = new DataInputView(stage, null, false);
        stage.getScene().setRoot(dataInputView.getRoot());
    }

    /**
     * Obsługuje generowanie wykresu Gantta z istniejącego harmonogramu.
     *
     * Wczytuje plik JSON z harmonogramem i jeśli wykres Gantta nie istnieje,
     * generuje go za pomocą PythonService.
     */
    private void handleGenerateGantt() {
        FileChooser fileChooser = new FileChooser();
        fileChooser.setTitle("Wybierz plik z harmonogramem");
        fileChooser.getExtensionFilters().add(
                new FileChooser.ExtensionFilter("Pliki JSON", "*.json")
        );

        File file = fileChooser.showOpenDialog(stage);
        if (file != null) {
            try {
                String json = Files.readString(file.toPath());
                ScheduleResult result = ScheduleResult.fromJson(json);

                String ganttPath = result.getGantDiagram();
                boolean ganttExists = ganttPath != null && Files.exists(Paths.get(ganttPath));

                if (!ganttExists) {
                    System.out.println("[MainMenuView] Wykres Gantta nie istnieje, generuję nowy...");

                    String pythonProjectPath = "C:\\inz\\Python";
                    PythonService pythonService = new PythonService(pythonProjectPath);

                    try {
                        Path generatedGantt = pythonService.generateGanttChart(file.getAbsolutePath());
                        System.out.println("[MainMenuView] Wygenerowano wykres: " + generatedGantt);

                        json = Files.readString(file.toPath());
                        result = ScheduleResult.fromJson(json);
                    } catch (Exception e) {
                        System.err.println("[MainMenuView] Nie udało się wygenerować wykresu Gantta: " + e.getMessage());
                        e.printStackTrace();
                    }
                }

                showResults(result, "existing");
            } catch (Exception ex) {
                showError("Błąd wczytywania harmonogramu: " + ex.getMessage());
            }
        }
    }

    private void showAlgorithmSelection(ProblemInstance instance) {
        AlgorithmSelectionView view = new AlgorithmSelectionView(stage, instance);
        stage.getScene().setRoot(view.getRoot());
    }

    private void showResults(ScheduleResult result, String algorithm) {
        ResultsView view = new ResultsView(stage, result, algorithm);
        stage.getScene().setRoot(view.getRoot());
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
     * Zwraca główny kontener widoku.
     *
     * @return Kontener BorderPane z kompletnym układem widoku menu
     */
    public Parent getRoot() {
        return root;
    }
}
