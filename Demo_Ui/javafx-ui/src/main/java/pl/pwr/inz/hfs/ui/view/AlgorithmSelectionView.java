package pl.pwr.inz.hfs.ui.view;

import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Parent;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.scene.layout.BorderPane;
import javafx.scene.layout.HBox;
import javafx.scene.layout.VBox;
import javafx.stage.Stage;
import pl.pwr.inz.hfs.ui.model.ProblemInstance;

import java.io.InputStream;

/**
 * Widok wyboru algorytmu optymalizacyjnego.
 *
 * Prezentuje użytkownikowi trzy dostępne algorytmy rozwiązywania
 * problemu HFS-SDST: Branch and Bound, Min Setup Time First oraz Tabu Search.
 * Zawiera ostrzeżenie dla algorytmu B&B przy dużej liczbie zadań.
 */
public class AlgorithmSelectionView {

    private final Stage stage;
    private final BorderPane root;
    private ProblemInstance instance;

    /**
     * Konstruktor tworzący widok bez instancji problemu.
     *
     * @param stage Główne okno aplikacji
     */
    public AlgorithmSelectionView(Stage stage) {
        this(stage, null);
    }

    /**
     * Konstruktor tworzący widok z podaną instancją problemu.
     *
     * @param stage Główne okno aplikacji
     * @param instance Instancja problemu do rozwiązania (może być null)
     */
    public AlgorithmSelectionView(Stage stage, ProblemInstance instance) {
        this.stage = stage;
        this.instance = instance;
        this.root = createLayout();
    }

    /**
     * Tworzy główny układ widoku.
     *
     * @return Kontener BorderPane z sekcjami: header, center i footer
     */
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

    /**
     * Tworzy sekcję nagłówka z logo i tytułem.
     *
     * @return Kontener HBox z logo PWR i tytułem widoku
     */
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

        Label titleLabel = new Label("Wybór Algorytmu optymalizacyjnego");
        titleLabel.getStyleClass().add("title-text");
        titleBox.getChildren().add(titleLabel);

        header.getChildren().addAll(logoBox, titleBox);
        return header;
    }

    /**
     * Tworzy centralną sekcję z przyciskami wyboru algorytmu.
     *
     * @return Kontener HBox z trzema przyciskami algorytmów
     */
    private HBox createCenterPanel() {
        HBox center = new HBox(30);
        center.setAlignment(Pos.CENTER);
        center.setPadding(new Insets(40));

        Button bnbButton = createAlgorithmButton(
                "Branch and Bound",
                "Algorytm dokładny\nZłożoność: O(n!)\nEfektywny do ~8 zadań",
                "bnb"
        );

        Button greedyButton = createAlgorithmButton(
                "Min Setup Time First",
                "Algorytm Heurystyczny\nZłożoność: O(n²)\nSzybki dla dużych instancji",
                "greedy"
        );

        Button tabuButton = createAlgorithmButton(
                "Tabu Search",
                "Algorytm metaheurystyczny\nZłożoność: O(n² × iteracje)\nDobry kompromis jakość/czas",
                "tabu"
        );

        center.getChildren().addAll(bnbButton, greedyButton, tabuButton);
        return center;
    }

    /**
     * Tworzy przycisk reprezentujący pojedynczy algorytm.
     *
     * @param name Nazwa algorytmu
     * @param description Opis algorytmu (złożoność, zastosowanie)
     * @param algorithmCode Kod algorytmu ("bnb", "greedy", "tabu")
     * @return Przycisk z obsługą wyboru algorytmu
     */
    private Button createAlgorithmButton(String name, String description, String algorithmCode) {
        VBox buttonContent = new VBox(10);
        buttonContent.setAlignment(Pos.CENTER);

        Label nameLabel = new Label(name);
        nameLabel.getStyleClass().add("algorithm-name");
        nameLabel.setWrapText(true);
        nameLabel.setMaxWidth(180);
        nameLabel.setAlignment(Pos.CENTER);

        Label descLabel = new Label(description);
        descLabel.getStyleClass().add("algorithm-description");
        descLabel.setWrapText(true);
        descLabel.setMaxWidth(180);
        descLabel.setAlignment(Pos.CENTER);

        buttonContent.getChildren().addAll(nameLabel, descLabel);

        Button button = new Button();
        button.setGraphic(buttonContent);
        button.getStyleClass().add("algorithm-button");
        button.setPrefWidth(220);
        button.setPrefHeight(180);

        button.setOnAction(e -> handleAlgorithmSelection(algorithmCode));

        return button;
    }

    /**
     * Tworzy sekcję stopki z przyciskiem powrotu i informacją o autorze.
     *
     * @return Kontener HBox ze stopką widoku
     */
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
        thesisLabel.setMaxWidth(700);
        thesisLabel.setAlignment(Pos.CENTER);

        footerContent.getChildren().addAll(authorLabel, thesisLabel);
        footer.getChildren().addAll(backButton, footerContent);
        return footer;
    }

    /**
     * Obsługuje wybór algorytmu przez użytkownika.
     *
     * Jeśli instancja problemu nie istnieje, przechodzi do widoku wprowadzania danych.
     * W przeciwnym razie ustawia algorytm i uruchamia optymalizację.
     * Wyświetla ostrzeżenie dla B&B przy liczbie zadań > 10.
     *
     * @param algorithmCode Kod wybranego algorytmu
     */
    private void handleAlgorithmSelection(String algorithmCode) {
        if (instance == null) {
            DataInputView dataInputView = new DataInputView(stage, algorithmCode, false);
            stage.getScene().setRoot(dataInputView.getRoot());
        } else {
            if ("bnb".equalsIgnoreCase(algorithmCode) && instance.getNumJobs() > 10) {
                javafx.scene.control.Alert alert = new javafx.scene.control.Alert(
                        javafx.scene.control.Alert.AlertType.WARNING
                );
                alert.setTitle("Ostrzeżenie");
                alert.setHeaderText("Algorytm Branch & Bound może działać bardzo długo!");
                alert.setContentText("Dla " + instance.getNumJobs() + " zadań algorytm Branch & Bound " +
                        "może potrzebować bardzo dużo czasu (nawet kilka godzin).\n\n" +
                        "Zalecamy:\n" +
                        "- Zmniejszyć liczbę zadań do maksymalnie 10\n" +
                        "- Lub wybrać algorytm Tabu Search lub MinSTF\n\n" +
                        "Czy na pewno chcesz kontynuować z tym algorytmem?");

                javafx.scene.control.ButtonType continueBtn = new javafx.scene.control.ButtonType(
                        "Kontynuuj mimo to",
                        javafx.scene.control.ButtonBar.ButtonData.OK_DONE
                );
                javafx.scene.control.ButtonType cancelBtn = new javafx.scene.control.ButtonType(
                        "Anuluj",
                        javafx.scene.control.ButtonBar.ButtonData.CANCEL_CLOSE
                );

                alert.getButtonTypes().setAll(continueBtn, cancelBtn);

                java.util.Optional<javafx.scene.control.ButtonType> result = alert.showAndWait();
                if (result.isPresent() && result.get().getButtonData() ==
                        javafx.scene.control.ButtonBar.ButtonData.CANCEL_CLOSE) {
                    return;
                }
            }

            instance.setAlgorithm(algorithmCode);
            OptimizationProgressView progressView = new OptimizationProgressView(stage, instance);
            stage.getScene().setRoot(progressView.getRoot());
        }
    }

    /**
     * Obsługuje powrót do poprzedniego widoku.
     *
     * Przechodzi do widoku wprowadzania danych jeśli instancja istnieje,
     * w przeciwnym razie wraca do menu głównego.
     */
    private void goBack() {
        if (instance != null) {
            DataInputView dataInputView = new DataInputView(stage, null, false);
            stage.getScene().setRoot(dataInputView.getRoot());
        } else {
            MainMenuView mainMenuView = new MainMenuView(stage);
            stage.getScene().setRoot(mainMenuView.getRoot());
        }
    }

    /**
     * Zwraca główny kontener widoku.
     *
     * @return Kontener BorderPane z kompletnym układem widoku
     */
    public Parent getRoot() {
        return root;
    }
}
