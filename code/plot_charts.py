from matplotlib import pyplot as plt


class PlotChart:
    """
    Class that contains all the requirements graphing methods
    1. T_max  Chart
    2. Initial Rise Method Chart
    3. Summary chart with all calculated values
    """

    def __init__(self, folder_save_path):
        self.folder_save_path = folder_save_path

    @staticmethod
    def title_correction(title):
        """
        Method for correction the T_stop name
        :param title: Title that require transformation to correct form
        :return: Corrected title
        """
        title = str(title)
        forbidden_signs = """ \ / * ? : | > < "" " . """.strip()
        for sign in forbidden_signs.split(' '):
            if sign in str(title):
                title = str(title).replace(sign, '_')
        title = title.replace(' ', '_')
        return title

    def t_max_stop(self, data_points, t_max, title, institute_bool):
        """
        This method creates a chart with temperatures and intensity from measurements data with selected T_max point.

        :param data_points: DataFrame with data to plot
        :param t_max: Calculated T_max value
        :param title: Title of the plot
        :param institute_bool: True/False if data came from INTiBS (Only for title)
        :return: Save charts into path given in class constructor
        """
        fig, ax = plt.subplots(figsize=(15, 8))
        ax.scatter(data_points['Temp'], data_points['Int'])
        ax.vlines(t_max, data_points['Int'].min(), data_points['Int'].max(), color='black', linestyles='dashed')
        ax.set_xlabel('Temperature [\u00b0C]', fontsize='13')
        ax.set_ylabel('Intensity (Arb. Units)', fontsize='13')
        if institute_bool is True:
            ax.set_title('T_max: ' + str(t_max) + ' [\u00b0C]' + ' - ' + str(title) + ' [\u00b0C]', fontsize=14)
        else:
            ax.set_title('T_max: ' + str(t_max) + ' [\u00b0C]' + ' - T_stop: ' + str(title) + ' [\u00b0C]', fontsize=14)

        title = PlotChart.title_correction(title)
        title_save = '/' + str(title) + '_TSTOP.png'
        title_save_path = str(self.folder_save_path) + title_save
        plt.savefig(title_save_path)

    def initial_rise(self, title, raw_data, median_data, points_selected, x_line, y_line):
        """
        Method creates and saves two graphs.
        The first one called 'IRM_TI' is created by selecting data points from Temperature vs Intensity.
        The second is created by picking points from the first graph and converted to log(Int) and 1/kT (IRM)
        and fit a linear regression line corresponding to the depth of the trap.

        :param title: Title of the plot
        :param raw_data: DataFrame from (Data Set)
        :param median_data: DataFrame with median data points corresponding to raw_data
        :param points_selected: DataFrame with values that meet the conditions IRM (15 % of max Intensity)
        :param x_line: DataFrame with x_axis-fitted values (Temperature transformed to  1/kT ) Linear regression points
        :param y_line: List of y_axis-fitted values (Intensity transformed to Log(Int)) Linear regression points.
        :return: Save charts into path given in class constructor
        """
        title = PlotChart.title_correction(title)
        title_initial_int_vs_temp = '/' + title + '_IRM_TI.png'
        fig, ax = plt.subplots(figsize=(15, 8))
        ax.scatter(raw_data['Temp'], raw_data['Int'], color='blue', label='Original data points')
        ax.scatter(median_data['round_temp'], median_data['Int'], color='orange', label='Median data points')
        ax.scatter(points_selected['round_temp'], points_selected['Int'], color='green', label='Selected points')
        ax.set_title('Initial Rise Method - Intensity vs Temperature', fontsize=14)
        ax.set_xlabel('Temperature [\u00b0C]', fontsize='13')
        ax.set_ylabel('Intensity (Arb. Units)', fontsize='13')
        ax.legend()
        save_path = str(self.folder_save_path) + title_initial_int_vs_temp
        plt.savefig(save_path)

        title_initial_lni_vs_kt = '/' + title + '_IRM_lnkT.png'
        fig, ax = plt.subplots(figsize=(15, 8))
        ax.scatter(raw_data['1/kT'], raw_data['ln(I)'], label='Original')
        ax.scatter(points_selected['1/kT'], points_selected['ln(I)'], c='orange', label='Selected points')
        ax.plot(x_line['1/kT'], y_line, c='yellow', label='fitted_line', linestyle='dashed', linewidth=6)
        ax.set_title('Initial Rise Method - ln(Int) vs 1/KT', fontsize=14)
        ax.set_xlabel('1/kT', fontsize='13')
        ax.set_ylabel('ln(I)', fontsize='13')
        ax.legend()
        save_path = str(self.folder_save_path) + title_initial_lni_vs_kt
        plt.savefig(save_path)

    def t_max_stop_energy(self, t_stop, t_max, energy):
        """
        Create summary chart with T_stop on X-axis and (Energy & T_max) on Y-axis. All is presented in one chart with
        double axis.
        :param t_stop: List with T_stop values
        :param t_max: List with T_max values
        :param energy: List with Energy values
        :return: Save charts into path given in class constructor
        """
        fig, ax = plt.subplots(figsize=(15, 8))
        ax.scatter(t_stop, t_max, color='black')
        ax.set_title('T_max - T_stop & Activation Energy')
        ax.set_xlabel('T_stop', fontsize=13)
        ax.set_ylabel('T_max', fontsize=13)
        ax2 = ax.twinx()
        ax2.scatter(t_stop, energy, c='blue')
        ax2.set_ylabel('Energy', c='blue', fontsize=13)

        title_save_path = str(self.folder_save_path) + '/TmaxTstopEnergy.png'
        plt.savefig(title_save_path)
