import customtkinter
from graph_analysis import *
from file_organization import *
from plot_charts import *
from initial_rise_method import *
from pdf_file import *


class DesktopApp:

    def __init__(self):
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("blue")

        application = customtkinter.CTk()
        application.title('T_max - T_stop')
        application.geometry("300x200")

        def button_folder():
            """
            This function asks for a directory containing data created by INTiBS software.
            After selecting the directory, enter the number of the first PMT measurement and the HEAT measurement file.
            After a few seconds the window will automatically close.

            """

            folder_path = customtkinter.filedialog.askdirectory(title='Select folder to analysis')

            folder_app = customtkinter.CTk()
            folder_app.title('INTiBS Data Extraction')
            folder_app.geometry("400x200")

            def start():
                """
                This button starts data preprocessing (grouping by temperature, saving each measurement into new folder
                and extracting most important data from measurement files). In the end it creates one Excel file
                containing all measurement data called -Data_set.xlsx
                """
                first_pmt = entry_pmt.get()
                first_heat = entry_heater.get()
                new_data = DividingRawDataToFolders(folder_path)
                new_data.divide_data_TO_folders_sequence_position(first_pmt, first_heat)
                new_data.create_one_excel_file()

                folder_app.destroy()

            label_pmt = customtkinter.CTkLabel(master=folder_app, text='First PMT_measured file number: ')
            label_heat = customtkinter.CTkLabel(master=folder_app, text='First Heat_measured file number: ')

            entry_pmt = customtkinter.CTkEntry(master=folder_app, placeholder_text='0', width=40)
            entry_heater = customtkinter.CTkEntry(master=folder_app, placeholder_text='0', width=40)

            start_button = customtkinter.CTkButton(master=folder_app, text='Start', command=start)

            label_pmt.grid(row=0, column=0, padx=(5, 0), pady=(20, 10))
            label_heat.grid(row=1, column=0, padx=(5, 0), pady=(0, 10))

            entry_pmt.grid(row=0, column=1, padx=(5, 0), pady=(20, 10))
            entry_heater.grid(row=1, column=1, padx=(0, 0), pady=(0, 10))

            start_button.grid(row=3, column=0, padx=(5, 0), pady=(25, 10))

            folder_app.mainloop()

        def button_analysis():
            """
            Button analysis asks for Excel file that contains a full data frame with information about temperature,
            intensity and Temperature Stop (T_stop) in the header. After selecting your Excel file, the program will ask
             you about the Heating Rate parameter, after filling in all required information
             the program starts the analysis.

            In the beginning, the program will find a maximum temperature and based on this value the IRM
            (Initial Rise Method) will be applied to find the depth of the traps. All charts and calculated IRM
            values will be saved in new folders.

            """

            excel_file_path = customtkinter.filedialog.askopenfile(title='Select excel file to analysis',
                                                                   filetypes=[("Excel files", ".xlsx .xls")]).name
            analysis_app = customtkinter.CTk()
            analysis_app.title('Analysis program')
            analysis_app.geometry("300x200")

            def start():
                fine_format_file = CreatingFormatToAnalysis(excel_file_path)
                heat_rate = float(entry_heat_rate.get())

                # Creating a new chart folder and IRM results folder
                chart_folder = FolderCreator(excel_file_path)
                chart_folder.create_chart_folder('Charts')
                irm_folder = FolderCreator(excel_file_path)
                irm_folder.create_chart_folder('IRM_results')

                # Finding T_max, T_stop and saving information to folder
                t_max_all = []
                i_max_all = []
                energy_all = []
                uncertain_energy = []
                t_stop_all = fine_format_file.t_stop_data  # Like: 'T_stop 30' or '30'
                t_stop_iter = 0
                for data_frame in fine_format_file.final_data_frames:
                    analysis = PlotAnalysis(data_frame)
                    analysis.mean_of_intensity_points()
                    t_max, i_max = analysis.peak_finder()  # Finding T_max
                    t_max_all.append(t_max)
                    i_max_all.append(i_max)
                    data_plot = PlotChart(chart_folder.to_save_path)  # Create and save t_max plot
                    data_plot.t_max_stop(data_frame, t_max, t_stop_all[t_stop_iter],
                                         fine_format_file.institute_apparatus)

                    # Initial Rise Method
                    initial_rise_method = InitialRise(analysis.data_frame, t_max)
                    data_plot.initial_rise(t_stop_all[t_stop_iter], initial_rise_method.raw_data,
                                           initial_rise_method.data_median, initial_rise_method.mean_points_chosen,
                                           initial_rise_method.x_line, initial_rise_method.y_line)

                    IRMExcelResults(initial_rise_method.raw_data, irm_folder.to_save_path,
                                    PlotChart('None').title_correction(t_stop_all[t_stop_iter]))

                    energy_all.append(initial_rise_method.e)
                    uncertain_energy.append(initial_rise_method.a_uncertain)
                    t_stop_iter += 1

                # Data
                t_stop_values_all = TStopInterpreter(t_stop_all).temperatures
                summary_data_frame = pd.DataFrame({
                    'T_stop [\u00b0C]': t_stop_all,
                    'T_stop (value)': t_stop_values_all,
                    'T_max [\u00b0C]': t_max_all,
                    'Energy [ev]': energy_all,
                    'u(E) [eV]': uncertain_energy
                })
                k_const = 8.617333262145E-5
                summary_data_frame['s'] = (heat_rate * summary_data_frame['Energy [ev]'] / (
                            k_const * (summary_data_frame['T_max [\u00b0C]'] + 273.15) ** 2)) / np.exp(
                    -summary_data_frame['Energy [ev]'] / (k_const * (summary_data_frame['T_max [\u00b0C]']+273.15)))

                summary_data_frame['u(E)/E [%]'] = summary_data_frame['u(E) [eV]']/summary_data_frame['Energy [ev]']*100

                path_to_save_excel = chart_folder.folder_name + '/summary_data_frame.xlsx'
                summary_data_frame.to_excel(path_to_save_excel)

                PlotChart(chart_folder.to_save_path).t_max_stop_energy(t_stop_values_all, t_max_all, energy_all)

                CreatePDFSummaryFile(path_to_save_excel, chart_folder.to_save_path, chart_folder.folder_name)

                analysis_app.destroy()

            entry_heat_rate_label = customtkinter.CTkLabel(master=analysis_app, text='Enter heating rate: ')
            entry_heat_rate = customtkinter.CTkEntry(master=analysis_app, placeholder_text='0', width=40)
            start_button = customtkinter.CTkButton(master=analysis_app, text='Start', command=start)

            start_button.grid(row=1, column=0, padx=(5, 0), pady=(25, 10))
            entry_heat_rate.grid(row=0, column=1, padx=(0, 0), pady=(10, 10))
            entry_heat_rate_label.grid(row=0, column=0, padx=(5, 0), pady=(15, 10), sticky=customtkinter.NS)

            analysis_app.mainloop()

        button_int = customtkinter.CTkButton(master=application, text='INTiBS folder', command=button_folder)
        button_ana = customtkinter.CTkButton(master=application, text='Analysis', command=button_analysis)

        button_int.grid(row=0, column=0, padx=(10, 10), pady=(50, 20))
        button_ana.grid(row=1, column=0, padx=(10, 10), pady=(10, 20))

        application.grid_columnconfigure(0, weight=1)
        application.pack_propagate(False)
        application.mainloop()


if __name__ == "__main__":
    DesktopApp()
