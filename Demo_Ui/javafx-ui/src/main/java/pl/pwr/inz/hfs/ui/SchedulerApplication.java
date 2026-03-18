package pl.pwr.inz.hfs.ui;

import javafx.application.Application;
import javafx.scene.Scene;
import javafx.scene.image.Image;
import javafx.stage.Stage;
import pl.pwr.inz.hfs.ui.view.MainMenuView;
import pl.pwr.inz.hfs.ui.service.PythonService;
import java.io.File;

/**
 * Główna klasa aplikacji JavaFX.
 *
 * Aplikacja wspomagająca harmonogramowanie produkcji dla problemu HFS-SDST
 * z efektem uczenia. Sprawdza dostępność Pythona, inicjalizuje interfejs użytkownika
 * oraz zarządza cyklem życia aplikacji.
 *
 * @author Bartłomiej Kuk
 * @version 1.0
 */
public class SchedulerApplication extends Application {

    private static final String APP_TITLE = "PWR - Harmonogramowanie Produkcji HFS";
    private static final int WINDOW_WIDTH = 1000;
    private static final int WINDOW_HEIGHT = 700;

    /**
     * Inicjalizuje i uruchamia aplikację.
     *
     * Sprawdza dostępność Pythona, tworzy główny widok, konfiguruje okno
     * i dodaje hook czyszczący folder wyników przy zamknięciu.
     *
     * @param primaryStage Główna scena aplikacji JavaFX
     */
    @Override
    public void start(Stage primaryStage) {
        try {
            if (!checkPythonAvailability()) {
                showErrorAndExit(
                    "Python nie jest zainstalowany lub nie jest dostępny w PATH.\n\n" +
                    "Aby uruchomić aplikację:\n" +
                    "1. Zainstaluj Python 3.8 lub nowszy z https://www.python.org/downloads/\n" +
                    "2. Podczas instalacji zaznacz opcję 'Add Python to PATH'\n" +
                    "3. Zrestartuj komputer i uruchom aplikację ponownie"
                );
                return;
            }

            MainMenuView mainMenuView = new MainMenuView(primaryStage);
            Scene scene = new Scene(mainMenuView.getRoot(), WINDOW_WIDTH, WINDOW_HEIGHT);

            String css = getClass().getResource("/styles/application.css").toExternalForm();
            scene.getStylesheets().add(css);

            primaryStage.setTitle(APP_TITLE);
            primaryStage.setScene(scene);
            primaryStage.setMinWidth(800);
            primaryStage.setMinHeight(600);

            primaryStage.setMaximized(true);
            primaryStage.setFullScreen(false);

            try {
                primaryStage.getIcons().add(new Image(getClass().getResourceAsStream("/images/pwr_logo.png")));
            } catch (Exception e) {
                System.out.println("Nie można załadować ikony aplikacji");
            }

            primaryStage.setOnCloseRequest(event -> {
                try {
                    String pythonPath = new File("../Python").getCanonicalPath();
                    PythonService pythonService = new PythonService(pythonPath);
                    pythonService.cleanResultsFolder();
                } catch (Exception e) {
                    System.err.println("Błąd podczas czyszczenia folderu results: " + e.getMessage());
                }
            });

            primaryStage.show();

        } catch (Exception e) {
            e.printStackTrace();
            showErrorAndExit("Błąd inicjalizacji aplikacji: " + e.getMessage());
        }
    }

    /**
     * Sprawdza czy Python jest dostępny w systemie.
     *
     * Próbuje uruchomić komendy 'python --version' i 'python3 --version'
     * w celu weryfikacji dostępności interpretera Pythona.
     *
     * @return true jeśli Python jest dostępny, false w przeciwnym razie
     */
    private boolean checkPythonAvailability() {
        try {
            ProcessBuilder pb = new ProcessBuilder("python", "--version");
            pb.redirectErrorStream(true);
            Process process = pb.start();
            int exitCode = process.waitFor();

            if (exitCode == 0) {
                return true;
            }

            pb = new ProcessBuilder("python3", "--version");
            pb.redirectErrorStream(true);
            process = pb.start();
            exitCode = process.waitFor();

            return exitCode == 0;

        } catch (Exception e) {
            System.err.println("Błąd podczas sprawdzania Pythona: " + e.getMessage());
            return false;
        }
    }

    /**
     * Wyświetla okno dialogowe z błędem krytycznym i kończy aplikację.
     *
     * @param message Treść komunikatu o błędzie
     */
    private void showErrorAndExit(String message) {
        javafx.scene.control.Alert alert = new javafx.scene.control.Alert(
            javafx.scene.control.Alert.AlertType.ERROR
        );
        alert.setTitle("Błąd krytyczny");
        alert.setHeaderText("Nie można uruchomić aplikacji");
        alert.setContentText(message);
        alert.showAndWait();
        System.exit(1);
    }

    /**
     * Punkt wejścia aplikacji.
     *
     * @param args Argumenty wiersza poleceń
     */
    public static void main(String[] args) {
        launch(args);
    }
}
