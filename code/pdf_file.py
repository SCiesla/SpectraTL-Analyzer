import numpy as np
from fpdf import FPDF
import datetime as dt
import plot_charts as pch
import pandas as pd


class CreatePDFSummaryFile:
    """
    This class creates report file with summary table and also shows the most important graphs
    """
    def __init__(self, summary_data, path_to_charts, path_to_save_report):
        self.summary_data = pd.read_excel(summary_data)
        t_stop_data = list(self.summary_data['T_stop [°C]'])
        self.summary_data.drop(['Unnamed: 0', 'T_stop [°C]'], axis=1, inplace=True)
        self.summary_data = np.round(self.summary_data, 3)
        self.path_to_charts = path_to_charts
        self.path_to_save_report = path_to_save_report

        # Daytime time data

        time_now = dt.datetime.now()
        formatted_time = time_now.strftime("%d-%m-%Y %H:%M")

        # Start pdf

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True)
        pdf.add_page()
        # Put day time to pdf
        pdf.set_font('times', '', 11)
        pdf.cell(150, 10, '')
        pdf.cell(20, 10, str(formatted_time))
        pdf.ln(30)

        # Header
        pdf.set_font('times', 'B', 24)
        pdf.cell(0, 0, 'Tmax - Tstop Analysis Report', align='C')
        pdf.ln(20)

        # Summary_graph
        pdf.image(str(self.path_to_charts) + '/TmaxTstopEnergy.png', w=200, h=120)

        # Create table name
        pdf.ln(5)
        pdf.set_font('times', '', 14)
        pdf.cell(83, 10, '')
        pdf.cell(0, 0, 'Summary table', align='B', ln=1)
        pdf.ln(5)

        # Create column names
        pdf.set_font('times', '', 11)
        n_iter = 1
        pdf.cell(10, 10, '')
        for col_name in self.summary_data.columns:
            pdf.cell(30 * n_iter, 10, txt=col_name, border=1, align='C')
        pdf.ln()

        # Adding rows and fill the table
        for row_number in range(0, len(self.summary_data)):
            pdf.cell(10, 10, '')
            row_data = list(self.summary_data.loc[row_number])
            for element in row_data:
                pdf.cell(30 * n_iter, 10, txt=str(element), border=1, align='C')
            pdf.ln()

        # Adding graphs
        pdf.set_font('times', 'B', 18)
        pdf.ln(10)

        plot_title = pch.PlotChart('PathNotNeeded')
        for t_stop in t_stop_data:
            pdf.cell(0, 0, str(t_stop), align='C', ln=1)
            pdf.ln(5)
            our_plot = str(self.path_to_charts) + '/' + str(plot_title.title_correction(t_stop)) + '_TSTOP.png'
            pdf.image(our_plot, w=200, h=120)
            pdf.ln(5)
            our_plot2 = str(self.path_to_charts) + '/' + str(plot_title.title_correction(t_stop)) + '_IRM_lnkT.png'
            pdf.image(our_plot2, w=200, h=120)
            pdf.ln(10)

        pdf.output(str(self.path_to_save_report) + '/Report.pdf')
