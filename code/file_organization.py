import os
import pandas as pd


class DividingRawDataToFolders:
    """
    The INTiBS software has a specific order of measurements. Each measurement has a step number at the end of the
    file name. The data with the word “PMT_measured” contains Intensity. The data with the word “Heater_measured”
    contains Temperature data.

    The data with information about Stop Temperature (IRM) is saved in a file which is two files before PMT measurement.
     (e.g, when the PMT number is 5 then information about Tstop is saved in file number 3).
     This class first takes the path to INTiBS folder with measurements. Then using the specific method,
     you can extract the data that we are interested in.
    """

    def __init__(self, path_of_folder):

        self.path_of_folder = path_of_folder
        self.list_of_files_in_folder = []
        self.paths_to_sub_folders = []
        self.combine_path = []

        # Creates a list of files all in given path and save it into array list_of_files_in_folder
        for entry in os.scandir(self.path_of_folder):
            if entry.is_file():
                self.list_of_files_in_folder.append(entry.name)

    def divide_data_TO_folders_sequence_position(self, first_pmt, first_heat):  # name of function to change!!!
        """
        This method sorts all csv data files and extracts information about temperature, intensity and t_stop
        temperature (required for thermal cleaning algorithm) and saves it afterwards into separate folders dividing
        the data by Sequence position and Irradiation time.

        :param first_pmt: Number of first PMT file that contains the intensity data
        :param first_heat: Number of first heat file that contains the temperature data corresponds to the first PMT
        :return: Saved temperature/intensity Excel files separated by T_stop name
        """
        # Sorting to obtain numerical order
        self.list_of_files_in_folder.sort()
        # Creating first numbers to start analysis
        initial_number_file_PMT = int(first_pmt)
        initial_number_file_HM = int(first_heat)
        step_between_PMT_HM = initial_number_file_HM - initial_number_file_PMT

        # Converting int number to numbers that are in folder example: 1->0001, 12 -> 0012
        # return string file number
        def number_converter(number):
            if number < 10:
                file_number = f'000{number}'
            elif 10 < number < 100:
                file_number = f'00{number}'
            else:
                file_number = f'0{number}'
            return file_number

        # Calculate difference between PMT files
        # to obtain a step_number
        def PMT_step():

            pmt_files = []
            for file_name_pmt in self.list_of_files_in_folder:
                if str(file_name_pmt)[5:8] == 'PMT':
                    pmt_files.append(file_name_pmt)

            pmt_files.sort()
            pmt_first = int(str(pmt_files[0])[:4])
            pmt_second = int(str(pmt_files[1])[:4])

            return pmt_second - pmt_first

        # Diff between files PMT
        next_pmt_file_number = PMT_step()

        # Actual number of PMT files
        actual_number_of_file_number = initial_number_file_PMT

        # Iteration for each file in given folder
        for file_name in self.list_of_files_in_folder:

            actual_number_of_file_txt = number_converter(actual_number_of_file_number)  # only for PMT files

            if str(file_name)[:4] == actual_number_of_file_txt:  # Taking first PMT file
                path_to_file = f'{self.path_of_folder}/{file_name}'
                data_table = pd.read_table(path_to_file, header=None, skip_blank_lines=True)

                # Static data
                time_intensity_data = []
                intensity_data = []
                time_temperature_data = []
                temperature_data = []
                t_stop = str()

                sequence_position = str(data_table.iloc[15, 0]).split(';')[-1]
                irradiation = str(data_table.iloc[28, 0]).split(';')[-1]

                # Extraction Time and Intensity from PMT file

                for data in data_table.iloc[44:, 0]:
                    time = float(str(data).split(',')[0])
                    intensity = float(str(data).split(',')[-1])
                    time_intensity_data.append(time)
                    intensity_data.append(intensity)

                # Extraction Temperature data from file Heater_measured
                temp_number_related_to_PMT = int(actual_number_of_file_txt) + step_between_PMT_HM
                for file_name_temp in self.list_of_files_in_folder:

                    if str(file_name_temp)[:4] == number_converter(
                            temp_number_related_to_PMT):
                        path_to_file_temp = f'{self.path_of_folder}/{file_name_temp}'
                        data_table_temp = pd.read_table(path_to_file_temp, header=None, skip_blank_lines=True)

                        for data_temp in data_table_temp.iloc[41:, 0]:
                            time = float(str(data_temp).split(',')[0])
                            heat = float(str(data_temp).split(',')[-1])
                            time_temperature_data.append(time)
                            temperature_data.append(heat)

                # Extract T_stop information
                t_stop_temperature = int(actual_number_of_file_txt) - 2
                for file_name_temp_pre in self.list_of_files_in_folder:

                    if str(file_name_temp_pre)[:4] == number_converter(
                            t_stop_temperature):
                        path_to_file_temp_stop = f'{self.path_of_folder}/{file_name_temp_pre}'
                        data_table_temp = pd.read_table(path_to_file_temp_stop, header=None, skip_blank_lines=True)
                        t_stop = str(data_table_temp.iloc[38, 0]).split(',')[-1]

                # Creating sequence_position folder SEQ-> IRR
                sequence_position_path = str(self.path_of_folder) + '/Sequence_position_' + sequence_position
                if not os.path.exists(sequence_position_path):
                    os.makedirs(sequence_position_path)

                # Creating irradiation folder
                irradiation_path = sequence_position_path + '/Irradiation_' + irradiation + '/Excel_files'
                if not os.path.exists(irradiation_path):
                    os.makedirs(irradiation_path)
                    self.paths_to_sub_folders.append(irradiation_path)  # adding path
                    self.combine_path = sequence_position_path + '/Irradiation_' + irradiation

                # Making two data_frames
                data_frame_PMT = pd.DataFrame({'Time': time_intensity_data, 'Intensity': intensity_data})
                data_frame_Heat_measurement = pd.DataFrame(
                    {'Time': time_temperature_data, 'Temperature': temperature_data})

                # Merging two dataframes by right-join on Time value and saving that in folder.
                data_frame = data_frame_Heat_measurement.merge(data_frame_PMT, how='right', on='Time')
                new_file_path = f'{irradiation_path}/{t_stop}.xlsx'
                time_temp_irr_data_frame = pd.DataFrame(data_frame)
                time_temp_irr_data_frame.to_excel(new_file_path, index=False)

                actual_number_of_file_number += next_pmt_file_number

    def create_one_excel_file(self):
        """
        This method combines all data frames into one Excel file that will be used for future analysis.
        :return: Data_set.xlsx file
        """
        # Create a all_data_frame excel file with all data in folder
        if len(self.paths_to_sub_folders) > 0:
            for path in self.paths_to_sub_folders:

                data_frames = []
                level_column_name = []
                files_list = os.listdir(path)
                files_list = [str(files_without_xlsx).split('.')[0] for files_without_xlsx in files_list]
                files_list = [int(x) for x in files_list]
                files_list.sort()

                for excel_file_name in files_list:
                    path_to_excel_file = str(path) + '/' + str(excel_file_name) + '.xlsx'
                    excel_data_frame = pd.read_excel(path_to_excel_file)
                    data_frames.append(excel_data_frame.iloc[:, 1:])
                    level_name = f'''T_stop: {str(excel_file_name).split('.')[0]}'''
                    level_column_name.append(level_name)

                all_data_frames = pd.concat([df for df in data_frames], axis=1,
                                            keys=level_column_name)

                combined_file_path = str(self.combine_path) + '/Data_set.xlsx'
                all_data_frames.to_excel(combined_file_path)


class TStopInterpreter:
    """
    Converting temperature to float type from messy Excel file
    """
    def __init__(self, data_list):

        temperatures = []
        for element in data_list:
            element_split = str(element).split(' ')
            for split_word in element_split:
                try:
                    temperature = float(split_word)
                    temperatures.append(temperature)
                    break
                except ValueError:
                    continue

        self.temperatures = temperatures


class FolderCreator:
    """
    This class creates required folders (for example chart-folder)
    """
    def __init__(self, path):
        self.path = path
        self.to_save_path = 0
        self.folder_name = os.path.dirname(path)

    def create_chart_folder(self, folder_name):
        folder_path_name = os.path.dirname(self.path)
        folder_path = str(folder_path_name)+'/'+folder_name
        chart_folder_exist = os.path.exists(folder_path)
        if chart_folder_exist is False:
            os.makedirs(folder_path)
        else:
            dir_list = os.listdir(folder_path_name)
            dir_chart_list = [folder for folder in dir_list if folder_name in str(folder)]
            number_of_charts_folders = len(dir_chart_list)
            folder_path += f'{int(number_of_charts_folders)}'
            os.makedirs(folder_path)

        self.to_save_path = folder_path


class IRMExcelResults:
    """
    Saving data frame with transformed temperature and intensity
    """
    def __init__(self, dataframe,  path_to_save, title_result):

        data_frame_results = pd.DataFrame({
            '1/kT': dataframe['1/kT'],
            'ln(I)': dataframe['ln(I)']
        })

        save_path = path_to_save + '/' + str(title_result) + '_IRM.xlsx'
        data_frame_results.to_excel(save_path)
