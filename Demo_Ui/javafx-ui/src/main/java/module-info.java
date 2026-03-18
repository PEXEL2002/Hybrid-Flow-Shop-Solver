/**
 * Moduł aplikacji HFS Scheduler.
 *
 * Aplikacja wspomagająca harmonogramowanie produkcji dla problemu
 * Hybrid Flow Shop z czasami przezbrojeń zależnymi od sekwencji
 * i efektem uczenia (HFS-SDST).
 */
module pl.pwr.inz.hfs.ui {
    requires javafx.controls;
    requires javafx.fxml;
    requires com.google.gson;

    opens pl.pwr.inz.hfs.ui to javafx.fxml;
    opens pl.pwr.inz.hfs.ui.view to javafx.fxml;
    opens pl.pwr.inz.hfs.ui.model to com.google.gson;

    exports pl.pwr.inz.hfs.ui;
    exports pl.pwr.inz.hfs.ui.view;
    exports pl.pwr.inz.hfs.ui.model;
    exports pl.pwr.inz.hfs.ui.service;
}
