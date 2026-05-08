"""Generates reports/kevser_documentation.pdf"""

from fpdf import FPDF
from pathlib import Path

OUTPUT = Path("reports/kevser_documentation.pdf")

# ── Colour palette ────────────────────────────────────────────────────────────
RED   = (225,  6,  0)   # F1 red
DARK  = ( 30, 30, 30)
GREY  = ( 80, 80, 80)
LIGHT = (245, 245, 245)
WHITE = (255, 255, 255)
LINE  = (210, 210, 210)


class PDF(FPDF):

    def header(self):
        # Red top bar
        self.set_fill_color(*RED)
        self.rect(0, 0, 210, 14, "F")
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*WHITE)
        self.set_xy(10, 4)
        self.cell(0, 6, "F1 Performance Analysis -- Kevser's Part Documentation", new_x="RIGHT", new_y="TOP")
        self.set_xy(0, 4)
        self.cell(200, 6, "src/main.py  |  notebooks/01_eda_and_preprocessing.ipynb", align="R")
        self.ln(10)

    def footer(self):
        self.set_y(-12)
        self.set_fill_color(*RED)
        self.rect(0, self.get_y(), 210, 12, "F")
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*WHITE)
        self.cell(0, 12, f"Page {self.page_no()}", align="C")

    # ── helpers ───────────────────────────────────────────────────────────────

    def chapter_title(self, text):
        self.ln(4)
        self.set_fill_color(*RED)
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", 13)
        self.cell(0, 9, f"  {text}", ln=True, fill=True)
        self.ln(3)
        self.set_text_color(*DARK)

    def section_title(self, text):
        self.ln(3)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*RED)
        self.cell(0, 7, text, ln=True)
        self.set_draw_color(*RED)
        self.set_line_width(0.4)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)
        self.set_text_color(*DARK)

    def sub_title(self, text):
        self.ln(2)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*DARK)
        self.cell(0, 6, text, ln=True)
        self.set_text_color(*DARK)

    def body(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*GREY)
        self.multi_cell(0, 5.5, text)
        self.ln(1)

    def code_block(self, text):
        self.ln(1)
        self.set_fill_color(*LIGHT)
        self.set_draw_color(*LINE)
        self.set_font("Courier", "", 8.5)
        self.set_text_color(20, 20, 120)
        self.set_line_width(0.3)
        lines = text.split("\n")
        padding = 3
        self.set_x(10)
        self.cell(190, padding, "", ln=True, border="LRT", fill=True)
        for line in lines:
            self.set_x(10)
            self.cell(190, 5, f"  {line}", ln=True, border="LR", fill=True)
        self.set_x(10)
        self.cell(190, padding, "", ln=True, border="LRB", fill=True)
        self.ln(2)
        self.set_text_color(*DARK)

    def info_box(self, label, text):
        self.ln(1)
        self.set_fill_color(255, 243, 243)
        self.set_draw_color(*RED)
        self.set_line_width(0.5)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*RED)
        self.set_x(10)
        self.cell(190, 6, f"  {label}", ln=True, border="LT", fill=True)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*GREY)
        self.set_x(10)
        self.multi_cell(190, 5, f"  {text}", border="LRB", fill=True)
        self.ln(2)
        self.set_text_color(*DARK)

    def table_row(self, cols, widths, header=False):
        if header:
            self.set_fill_color(*DARK)
            self.set_text_color(*WHITE)
            self.set_font("Helvetica", "B", 9)
        else:
            self.set_fill_color(*WHITE)
            self.set_text_color(*GREY)
            self.set_font("Helvetica", "", 9)
        self.set_draw_color(*LINE)
        self.set_line_width(0.2)
        for col, w in zip(cols, widths):
            self.cell(w, 7, f"  {col}", border=1, fill=True)
        self.ln()
        self.set_text_color(*DARK)

    def bullet(self, text, indent=14):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*GREY)
        self.set_x(indent)
        self.cell(5, 5.5, chr(149))
        self.multi_cell(0, 5.5, text)


# ═════════════════════════════════════════════════════════════════════════════

pdf = PDF()
pdf.set_auto_page_break(auto=True, margin=18)
pdf.set_margins(10, 18, 10)


# ── COVER PAGE ───────────────────────────────────────────────────────────────
pdf.add_page()

pdf.set_fill_color(*RED)
pdf.rect(0, 0, 210, 297, "F")

pdf.set_font("Helvetica", "B", 36)
pdf.set_text_color(*WHITE)
pdf.set_y(80)
pdf.cell(0, 18, "Kevser's Part", align="C", ln=True)

pdf.set_font("Helvetica", "", 16)
pdf.cell(0, 10, "Documentation", align="C", ln=True)

pdf.set_font("Helvetica", "", 11)
pdf.set_y(130)
pdf.cell(0, 8, "F1 Performance Analysis Project", align="C", ln=True)
pdf.cell(0, 8, "Model Evaluation & Diagnostics", align="C", ln=True)

pdf.set_fill_color(*WHITE)
pdf.rect(30, 175, 150, 0.5, "F")

pdf.set_font("Helvetica", "", 10)
pdf.set_y(185)
pdf.cell(0, 6, "Dataset: f1_2018_2024_wow_master_dataset.csv  (2018 - 2024)", align="C", ln=True)
pdf.cell(0, 6, "Train seasons: 2018 - 2023   |   Test season: 2024", align="C", ln=True)


# ── PAGE 2 - WHAT IS THIS PROJECT? ──────────────────────────────────────────
pdf.add_page()
pdf.chapter_title("1.  Big Picture -- What Is This Project?")

pdf.body(
    "This project uses Formula 1 race data from 2018 to 2024 to build a model that "
    "predicts where a driver will finish a race before it starts. The input is information "
    "that is known before the race -- like where the driver qualified, how they have been "
    "performing recently, and how reliable their car has been. The output is a predicted "
    "finish position (1st, 2nd, ... 20th)."
)

pdf.body(
    "The project is split between three contributors:"
)

pdf.bullet("Arda's parts: engineered the new feature (driver_season_momentum), produced three data insights, and created the EDA chart.")
pdf.bullet("Ceren's part: built and trained the linear regression model.")
pdf.bullet("Kevser's part: added driver_season_momentum into the model and built the three diagnostic charts to evaluate how well the model works.")

pdf.ln(2)
pdf.chapter_title("2.  Key Concepts Explained Simply")

pdf.section_title("What is EDA?")
pdf.body(
    "EDA stands for Exploratory Data Analysis. Before building any model, you look at the "
    "data to understand it -- find patterns, spot problems, and get a feel for the numbers. "
    "In this project, EDA includes things like: 'do drivers who qualify at the front actually "
    "finish at the front?' or 'do teams that break down more often finish worse?' Answering "
    "these questions visually and numerically before touching a model is called EDA."
)

pdf.section_title("What is Feature Engineering?")
pdf.body(
    "A 'feature' is any column you feed into a model as an input. Raw data rarely has exactly "
    "the columns you need, so you create new ones by combining or transforming existing columns. "
    "This is feature engineering."
)
pdf.body(
    "Example in this project: the dataset has a column for how many points a driver has earned "
    "this season and how many races they have run. Neither alone is very useful, but dividing "
    "one by the other gives you average points per race -- a much more meaningful signal. That "
    "new column is driver_season_momentum, and creating it is feature engineering."
)

pdf.section_title("What is a Linear Regression Model?")
pdf.body(
    "Linear regression is the simplest prediction model. It draws a straight line through "
    "your data and uses that line to make predictions. In this project the line is in "
    "multi-dimensional space (because there are 4 input features, not just 1), but the idea "
    "is the same: find a formula of the shape:"
)
pdf.code_block("predicted_finish = intercept\n"
               "                 + (coef_grid            * grid)\n"
               "                 + (coef_form            * driver_form_score)\n"
               "                 + (coef_readiness       * weekend_readiness)\n"
               "                 + (coef_momentum        * driver_season_momentum)")
pdf.body(
    "The model learns the five numbers (intercept and four coefficients) by looking at historical "
    "races (2018-2023). Then it uses those numbers to predict 2024 races it has never seen."
)

pdf.section_title("What is Model Evaluation / Diagnostics?")
pdf.body(
    "After a model makes predictions, you need to check how wrong it is and in what way. "
    "This is model evaluation. Diagnostic charts make the errors visual so you can quickly "
    "see whether the model is good overall, whether it is wrong in a systematic pattern, and "
    "which features are doing the most work. That is exactly what Kevser's part does."
)


# ── PAGE 3 - KEVSER'S CONTRIBUTION ──────────────────────────────────────────
pdf.add_page()
pdf.chapter_title("3.  Kevser's Contribution -- Overview")

pdf.body(
    "Kevser's part lives inside the KEVSER'S MODEL DIAGNOSTICS section of src/main.py "
    "(line 207 onwards) and the 'Kevser's Model Diagnostics' cell in the notebook. "
    "It does two things:"
)

pdf.info_box(
    "Contribution 1 -- Feature addition",
    "Added driver_season_momentum as the 4th input feature to Ceren's regression model. "
    "This is a one-line change in the feature list but it changes what the model learns."
)

pdf.info_box(
    "Contribution 2 -- plot_model_diagnostics function",
    "A function that takes the model's predictions and produces a three-panel diagnostic "
    "chart saved to reports/ceren_lr_diagnostics.png."
)


pdf.section_title("3.1  Adding driver_season_momentum to the Model")

pdf.sub_title("What the feature measures")
pdf.body(
    "driver_season_momentum = driver_season_points_before_race / driver_season_races_before_race"
)
pdf.body(
    "For each race row, this tells you: on average, how many championship points per race has "
    "this driver scored so far this season? A driver with momentum of 18 has been scoring 18 "
    "points per race -- roughly a podium every race. A driver with momentum of 2 has been "
    "struggling. Importantly, this only uses data from before the current race, so there is "
    "no data leakage (the model is not cheating by looking at future results)."
)
pdf.body(
    "For the first race of a season, the driver has run 0 races, so the division would be "
    "undefined. This is handled by replacing 0 with NaN and then filling NaN with 0, so "
    "the first race of the season always gets a momentum of 0."
)

pdf.sub_title("Why it helps the model")
pdf.body(
    "The original three features describe where a driver is starting (grid), how they "
    "performed recently in the last 3-5 races (driver_form_score), and how prepared they "
    "look for this specific weekend (weekend_readiness). What was missing was a season-level "
    "signal. Two drivers can have the same grid position but very different season stories -- "
    "one is fighting for the championship and one is a backmarker. driver_season_momentum "
    "captures that difference."
)

pdf.sub_title("Where it appears in the code")
pdf.code_block(
    "# main.py -- run_ceren_linear_regression(), line 279\n"
    "feature_columns = [\n"
    '    "grid",\n'
    '    "driver_form_score",\n'
    '    "weekend_readiness",\n'
    '    "driver_season_momentum",   # <-- Kevser\'s addition\n'
    "]"
)
pdf.body(
    "With this list, the regression fits 5 coefficients: one intercept plus one for each "
    "feature. The trained coefficient for driver_season_momentum is stored in beta[4] and "
    "is saved to reports/ceren_linear_regression_metrics.json under the 'coefficients' key."
)


# ── PAGE 4 - THE DIAGNOSTIC FUNCTION ─────────────────────────────────────────
pdf.add_page()
pdf.chapter_title("4.  The plot_model_diagnostics Function")

pdf.body(
    "This function is defined at main.py line 211. It is called once, at the very end of "
    "run_ceren_linear_regression, after all predictions have been made and saved. It takes "
    "the raw prediction arrays and the trained coefficients and turns them into a three-panel chart."
)

pdf.sub_title("Function signature")
pdf.code_block(
    "def plot_model_diagnostics(\n"
    "    actual:      np.ndarray,   # real 2024 finish positions from the dataset\n"
    "    predicted:   np.ndarray,   # model's predicted positions (clipped to 1-20)\n"
    "    beta:        np.ndarray,   # trained coefficients [intercept, c1, c2, c3, c4]\n"
    "    features:    list[str],    # feature names -- used as axis labels\n"
    "    output_path: Path,         # where to save the PNG\n"
    ") -> None"
)

pdf.sub_title("How residuals are computed")
pdf.body(
    "At the very start of the function, residuals are calculated:"
)
pdf.code_block("residuals = actual - predicted")
pdf.body(
    "A residual is the difference between what actually happened and what the model guessed. "
    "If a driver finished 8th and the model predicted 5th, the residual is 8 - 5 = +3. "
    "If the model predicted 10th and the driver finished 7th, the residual is -3. "
    "A perfect model would have all residuals equal to 0."
)

pdf.sub_title("How the figure is created")
pdf.code_block("fig, axes = plt.subplots(1, 3, figsize=(18, 5))")
pdf.body(
    "This creates one figure with three panels side by side. Each panel is then filled "
    "independently. At the end the whole figure is saved as a single PNG file."
)


# ── PAGE 5 - THREE PANELS ────────────────────────────────────────────────────
pdf.add_page()
pdf.chapter_title("5.  The Three Diagnostic Panels")

pdf.section_title("Panel 1 -- Actual vs. Predicted")

pdf.body(
    "Every dot on this scatter plot represents one race entry from the 2024 test set. "
    "Its X position is the real finish position and its Y position is what the model predicted."
)
pdf.code_block(
    "ax.scatter(actual, predicted, alpha=0.35, color='#E10600', s=18)\n"
    "ax.plot([1, 20], [1, 20], 'k--', linewidth=1, label='Perfect prediction')"
)
pdf.body(
    "The dashed diagonal line going from corner to corner is the 'perfect prediction' line. "
    "Any dot sitting exactly on that line means the model was 100% correct for that race. "
    "Dots above the line mean the model over-predicted (guessed a worse finish than reality). "
    "Dots below the line mean the model under-predicted (guessed a better finish than reality)."
)
pdf.body(
    "Both axes are locked to the range 1-20, which matches the possible finish positions in F1. "
    "The tighter the cloud of dots around the diagonal, the better the model."
)

pdf.info_box(
    "What to look for",
    "Tight cluster around the diagonal = accurate model.\n"
    "Wide scatter = high prediction error.\n"
    "Dots all bunched in one area (e.g. all predicted mid-pack) = the model is not distinguishing well between drivers."
)

pdf.section_title("Panel 2 -- Feature Coefficients")

pdf.body(
    "This horizontal bar chart shows the four learned coefficients -- one per feature. "
    "The intercept is deliberately excluded because it is just a baseline offset and does "
    "not tell you anything about the importance of the features."
)
pdf.code_block(
    "coef_vals = beta[1:]   # skip beta[0] which is the intercept\n"
    "colors = ['#E10600' if v > 0 else '#1f77b4' for v in coef_vals]\n"
    "bars = ax.barh(features, coef_vals, color=colors)"
)
pdf.body(
    "Red bar = positive coefficient: higher value for this feature pushes the predicted "
    "finish number up (towards the back of the grid). In F1, a higher finish number is worse "
    "(20th is last), so red features hurt predicted performance."
)
pdf.body(
    "Blue bar = negative coefficient: higher value for this feature pushes the predicted "
    "finish number down (towards the front). Blue features help predicted performance."
)
pdf.body(
    "The actual number printed on each bar (e.g. 0.412) means: for every 1-unit increase "
    "in this feature, the model adds 0.412 to the predicted finish position. For a negative "
    "coefficient like -0.317, every 1-unit increase moves the prediction 0.317 positions "
    "towards the front."
)

pdf.info_box(
    "What to look for",
    "Large coefficient magnitude = that feature has a big influence on predictions.\n"
    "Unexpected sign (e.g. momentum being positive/red) = worth investigating -- could mean the feature needs re-scaling or the relationship is being cancelled by another feature."
)

pdf.section_title("Panel 3 -- Residuals vs. Predicted")

pdf.body(
    "This is the most technical of the three panels and the most useful for spotting problems."
)
pdf.code_block(
    "ax.scatter(predicted, residuals, alpha=0.35, color='#1f77b4', s=18)\n"
    "ax.axhline(0, color='black', linewidth=1, linestyle='--')"
)
pdf.body(
    "The X axis is the predicted finish position. The Y axis is the residual (actual minus predicted). "
    "The horizontal dashed line at Y=0 is the ideal: if a dot sits on that line, the model "
    "was perfect for that entry."
)
pdf.body(
    "What you want to see is a random cloud of dots spread evenly above and below the zero line, "
    "with no clear pattern. Any pattern means the model is making systematic mistakes."
)

pdf.info_box(
    "What to look for",
    "Random scatter around 0 = model errors are random and the linear regression assumptions hold.\n"
    "Fan shape (errors getting bigger as predicted value increases) = the model is much less reliable for drivers predicted to finish at the back.\n"
    "Curve (dots arc above then below the line) = the relationship between features and finish is not actually linear; a more complex model may be needed.\n"
    "Cluster of large negative residuals at low predicted values = model consistently overestimates how well top drivers finish."
)


# ── PAGE 6 - OUTPUTS & FLOW ───────────────────────────────────────────────────
pdf.add_page()
pdf.chapter_title("6.  Outputs and Files")

pdf.body("Running main.py produces three files that Kevser's part contributes to:")
pdf.ln(2)

pdf.table_row(["File", "What's in it"], [120, 70], header=True)
pdf.table_row(["reports/ceren_lr_diagnostics.png", "The 3-panel diagnostic chart"], [120, 70])
pdf.table_row(["reports/ceren_linear_regression_metrics.json", "MAE, RMSE, R2, all 5 coefficients"], [120, 70])
pdf.table_row(["reports/ceren_linear_regression_predictions_2024.csv", "Row-by-row predictions + driver_season_momentum"], [120, 70])

pdf.ln(4)

pdf.section_title("Evaluation Metrics in the JSON (from Ceren's model, used by Kevser)")

pdf.table_row(["Metric", "Formula", "Meaning"], [40, 80, 70], header=True)
pdf.table_row(["MAE", "mean(|actual - predicted|)", "Average error in positions"], [40, 80, 70])
pdf.table_row(["RMSE", "sqrt(mean((actual - predicted)^2))", "Punishes large errors more"], [40, 80, 70])
pdf.table_row(["R2", "1 - SS_residual / SS_total", "0 = useless, 1 = perfect"], [40, 80, 70])

pdf.ln(4)

pdf.section_title("Execution Flow")
pdf.body("The order things happen when you run main.py:")

steps = [
    ("1", "Data loaded from CSV", "All 2018-2024 races"),
    ("2", "driver_season_momentum added", "Arda's feature engineering"),
    ("3", "Three insights printed", "Arda's EDA"),
    ("4", "EDA chart saved", "Arda's chart"),
    ("5", "build_features() called", "Ceren's feature prep (form score, weekend readiness)"),
    ("6", "run_ceren_linear_regression() called", "Ceren's model trains on 2018-2023, predicts 2024"),
    ("7", "driver_season_momentum used in fit", "Kevser's feature addition"),
    ("8", "Metrics + predictions saved to disk", "Ceren + Kevser output"),
    ("9", "plot_model_diagnostics() called", "Kevser's diagnostic chart generated"),
]
pdf.ln(1)
pdf.table_row(["Step", "What happens", "Who"], [18, 110, 62], header=True)
for s in steps:
    pdf.table_row(list(s), [18, 110, 62])


# ── PAGE 7 - READING THE CHART QUICK GUIDE ───────────────────────────────────
pdf.add_page()
pdf.chapter_title("7.  Quick Reading Guide -- How to Interpret the Chart")

pdf.body(
    "When you open reports/ceren_lr_diagnostics.png, here is how to read what you see:"
)
pdf.ln(2)

pdf.table_row(["What you see", "What it means"], [100, 90], header=True)
rows = [
    ("Dots tight on the diagonal (Panel 1)", "Model is accurate -- predictions close to reality"),
    ("Dots scattered far off diagonal", "High prediction error, model needs improvement"),
    ("All dots bunched in the middle", "Model is not separating good/bad finishers well"),
    ("All residuals near 0 (Panel 3)", "Errors are small and random -- good sign"),
    ("Fan shape in residuals", "Model less reliable for back-of-grid predictions"),
    ("Curved arc in residuals", "Relationship is not linear, more complex model needed"),
    ("Large red bar (Panel 2)", "That feature strongly predicts worse finishes"),
    ("Large blue bar", "That feature strongly predicts better finishes"),
    ("Unexpected sign on momentum", "May need feature scaling or further investigation"),
]
for r in rows:
    pdf.table_row(list(r), [100, 90])

pdf.ln(6)

pdf.section_title("Summary")
pdf.body(
    "Kevser's part answers the question: 'OK, the model made predictions -- but how good are they, "
    "and where does it go wrong?' Without diagnostic charts, you only have three summary numbers "
    "(MAE, RMSE, R2) and no visual sense of whether the errors are random or systematic. "
    "The three panels together give a complete picture: overall accuracy (Panel 1), "
    "which features drive the model (Panel 2), and whether the errors follow a pattern (Panel 3). "
    "The addition of driver_season_momentum means the model now accounts for a driver's "
    "broader season form, not just their last few races."
)

pdf.output(str(OUTPUT))
print(f"PDF saved → {OUTPUT}")
