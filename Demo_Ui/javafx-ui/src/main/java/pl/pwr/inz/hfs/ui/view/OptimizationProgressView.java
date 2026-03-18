package pl.pwr.inz.hfs.ui.view;

import javafx.application.Platform;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Parent;
import javafx.scene.control.Label;
import javafx.scene.control.ProgressIndicator;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.scene.layout.BorderPane;
import javafx.scene.layout.VBox;
import javafx.stage.Stage;
import pl.pwr.inz.hfs.ui.model.ProblemInstance;
import pl.pwr.inz.hfs.ui.model.ScheduleResult;
import pl.pwr.inz.hfs.ui.service.PythonService;

import java.io.InputStream;

/**
 * Widok postępu optymalizacji wyświetlany podczas wykonywania algorytmu szeregowania.
 *
 * Klasa odpowiada za prezentację ekranu postępu podczas przetwarzania instancji problemu.
 * Wyświetla logo PWR, informacje o wybranym algorytmie, parametrach instancji oraz wskaźnik
 * postępu. W tle uruchamia serwis optymalizacji w osobnym wątku, aby nie blokować interfejsu
 * użytkownika. Po zakończeniu optymalizacji automatycznie przechodzi do widoku wyników.
 *
 * W przypadku błędu podczas optymalizacji wyświetla okno dialogowe z informacją o błędzie
 * i umożliwia powrót do menu głównego.
 */
public class OptimizationProgressView {

    private final Stage stage;
    private final BorderPane root;
    private final ProblemInstance instance;

    /**
     * Konstruktor widoku postępu optymalizacji.
     *
     * @param stage scena główna aplikacji
     * @param instance instancja problemu do optymalizacji
     */
    public OptimizationProgressView(Stage stage, ProblemInstance instance) {
        this.stage = stage;
        this.instance = instance;
        this.root = createLayout();

        startOptimization();
    }

    private BorderPane createLayout() {
        BorderPane layout = new BorderPane();
        layout.setPadding(new Insets(20));

        VBox center = new VBox(20);
        center.setAlignment(Pos.CENTER);

        try {
            InputStream logoStream = getClass().getResourceAsStream("/images/pwr_logo.png");
            if (logoStream != null) {
                Image logoImage = new Image(logoStream);
                ImageView logoView = new ImageView(logoImage);
                logoView.setFitHeight(80);
                logoView.setPreserveRatio(true);
                center.getChildren().add(logoView);
            } else {
                Label logoLabel = new Label("PWR");
                logoLabel.getStyleClass().add("logo-text");
                center.getChildren().add(logoLabel);
            }
        } catch (Exception e) {
            Label logoLabel = new Label("PWR");
            logoLabel.getStyleClass().add("logo-text");
            center.getChildren().add(logoLabel);
        }

        Label statusLabel = new Label("Optymalizacja w toku...");
        statusLabel.getStyleClass().add("title-text");

        Label algorithmLabel = new Label("Algorytm: " + getAlgorithmName(instance.getAlgorithm()));
        algorithmLabel.getStyleClass().add("info-text");

        Label instanceLabel = new Label(String.format(
                "Instancja: %d zadań, %d etapów",
                instance.getNumJobs(),
                instance.getNumStages()
        ));
        instanceLabel.getStyleClass().add("info-text");

        ProgressIndicator progress = new ProgressIndicator();
        progress.setPrefSize(80, 80);

        Label waitLabel = new Label("Proszę czekać...");
        waitLabel.getStyleClass().add("help-text");

        center.getChildren().addAll(
                statusLabel,
                algorithmLabel,
                instanceLabel,
                progress,
                waitLabel
        );

        layout.setCenter(center);
        return layout;
    }

    private void startOptimization() {
        new Thread(() -> {
            try {
                String pythonPath = findPythonProjectPath();
                PythonService pythonService = new PythonService(pythonPath);
                ScheduleResult result = pythonService.runOptimization(instance);

                Platform.runLater(() -> {
                    ResultsView resultsView = new ResultsView(stage, result, instance.getAlgorithm(), instance);
                    stage.getScene().setRoot(resultsView.getRoot());
                });

            } catch (Exception e) {
                e.printStackTrace();
                Platform.runLater(() -> showError());
            }
        }).start();
    }

    private String findPythonProjectPath() {
        String[] possiblePaths = {
                "C:\\inz\\Python",
                "..\\..\\Python",
                "../Python",
                "../../Python",
                "C:\\Users\\barte\\Desktop\\test\\demo\\Python",
                "./Python"
        };

        for (String path : possiblePaths) {
            java.io.File file = new java.io.File(path, "main.py");
            if (file.exists()) {
                try {
                    return new java.io.File(path).getCanonicalPath();
                } catch (Exception e) {
                    return path;
                }
            }
        }

        return "..\\..\\Python";
    }

    private String getAlgorithmName(String code) {
        switch (code) {
            case "bnb":
                return "Branch and Bound";
            case "greedy":
                return "Greedy (MinSTF)";
            case "tabu":
                return "Tabu Search";
            default:
                return code;
        }
    }

    private void showError() {
        javafx.scene.control.Alert alert = new javafx.scene.control.Alert(
                javafx.scene.control.Alert.AlertType.ERROR
        );
        alert.setTitle("Błąd");
        alert.setHeaderText("Wystąpił błąd podczas wykonywania optymalizacji");

        String errorMessage = "Możliwe przyczyny błędu:\n" +
                              "• Uszkodzony plik wejściowy\n" +
                              "• Brak wymaganych bibliotek\n" +
                              "• Nieprawidłowa konfiguracja systemu";

        alert.setContentText(errorMessage);
        alert.showAndWait();

        MainMenuView mainMenuView = new MainMenuView(stage);
        stage.getScene().setRoot(mainMenuView.getRoot());
    }

    /**
     * Zwraca element główny (root) widoku.
     *
     * @return element BorderPane zawierający interfejs użytkownika widoku postępu
     */
    public Parent getRoot() {
        return root;
    }
}
