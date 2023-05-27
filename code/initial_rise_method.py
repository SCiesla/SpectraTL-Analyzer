import numpy as np
import pandas as pd


class InitialRise:
    """
    The Initial Rise Method implemented in Python. This Class is made to find a depth of the
    traps in persistent luminescence materials.
    """

    def __init__(self, data, t_max):
        self.k = 8.617333262145E-5  # Boltzmann constant [eV/K]

        # Selecting data lower than T_max and transform data to log(I) and 1/kT
        data = data.drop_duplicates()
        data = data[data['Temp'] <= t_max].copy()
        data.reset_index(drop=True, inplace=True)

        raw_data = data.copy()
        raw_data = raw_data[raw_data['Int'] > 1]  # Bo log
        raw_data['1/kT'] = 1 / ((raw_data['Temp'] + 273.15) * self.k)
        raw_data['ln(I)'] = np.log(raw_data['Int'])
        raw_data['round_temp'] = round(raw_data['Temp'])
        self.raw_data = raw_data

        data_median = pd.DataFrame(raw_data.groupby(by='round_temp').median()['Int'])
        data_median.reset_index(inplace=True)
        data_median['1/kT'] = 1 / ((data_median['round_temp'] + 273.15) * self.k)
        data_median['ln(I)'] = np.log(data_median['Int'])
        self.data_median = data_median

        # Data above 15% of max value

        i_min = data_median['Int'].min()
        i_max = data_median['Int'].max()
        i_value = (i_max - i_min) * 0.15 + i_min

        data_int_15 = raw_data[raw_data['Int'] <= i_value].copy()
        data_int_15.reset_index(drop=True, inplace=True)

        mean_points_chosen = data_median[data_median['Int'] <= i_value].copy()
        mean_points_chosen.sort_values(by='round_temp', inplace=True)
        mean_points_chosen.reset_index(drop=True, inplace=True)

        self.mean_points_chosen = mean_points_chosen

        def linear_function(x, a, b):
            return a * x + b

        def blind_fit(mean_points_blind_function):
            """
            The algorithm:

            1. Determine all possible linear functions on a given interval
            2. Fit these functions and calculate residuals
            3. Create a DataFrame containing columns-- first: number of data taking part in fitting,
            selected: data size with residues less or equal 0.1
            4. Create 'p' parameter which is a fraction of p = selected/len(all_data) => Fraction of significant data
            5. Create a difference between p values
            6. The p value will be increasing all the time because every next fitting line is more accurate than
            the previous one. However, when the fitted line has an L-shape we will observe a decreasing trend
            which means that we should take this ‘p’ value.

            :param mean_points_blind_function: Mean transformed data points 
            :return: slope and intercept of linear fitting 
            """

            # Specify data length, max and min points in function 
            data_l = len(mean_points_blind_function) - 1
            max_kT_value = mean_points_blind_function['1/kT'].loc[data_l]
            min_kT_value = mean_points_blind_function['1/kT'].loc[0]
            min_ln_value = mean_points_blind_function['ln(I)'].loc[0]

            kT_range = np.linspace(min_kT_value, max_kT_value, data_l)
            kT_range = kT_range[::-1]

            diff_sum = []
            a_values = []
            b_values = []
            kT_values = []

            data_length = []
            data_under1 = []

            # Checking all possible linear functions for each linear function
            # Calculate data length and residua
            for x_2 in kT_range:

                y_2 = mean_points_blind_function['ln(I)'].max()
                y_1 = mean_points_blind_function['ln(I)'].min()
                x_1 = mean_points_blind_function['1/kT'].min()

                if x_1 == x_2:
                    continue

                a = abs((y_2 - y_1) / (x_2 - x_1))
                b = y_2 - (-a) * x_1

                original = mean_points_blind_function.copy()

                fitted = [linear_function(x, -a, b) for x in original['1/kT']]
                df_fitted = pd.DataFrame(fitted, columns=['fitted'])
                original = pd.concat([original, df_fitted], axis=1)
                original['diff'] = abs(original['ln(I)'] - original['fitted'])

                original = original[original['fitted'] > min_ln_value].copy()

                data_all = len(original)
                data_under = len(original[original['diff'] <= 0.1])

                data_length.append(data_all)
                data_under1.append(data_under)

                diff_sum.append(original['diff'].sum())
                a_values.append(a)
                b_values.append(b)
                kT_values.append(x_2)

                # plt.scatter(mean_points_chosen['1/kT'], mean_points_chosen['ln(I)'])
                # plt.scatter(original['1/kT'], original['fitted'])
                # plt.show()

            # Data Frame with summary values 
            data_length_result = pd.DataFrame({'first': data_length, 'selected': data_under1,
                                               'a': a_values, 'b': b_values, 'kT': kT_values,
                                               'sum_error': diff_sum})
            data_length_result['p'] = data_length_result['selected'] / len(kT_range)
            
            data_length_result['p_diff'] = data_length_result['p'].diff()
    
            max_value = data_length_result['p'].max()
            max_p_index = data_length_result[data_length_result['p'] == max_value].index[0]

            index_count = 0
            for p_diff in data_length_result['p_diff']:  
                if p_diff < 0 and index_count < max_p_index:
                    max_value_supp = data_length_result['p'].loc[index_count - 1]
                    if max_value_supp > 0.05:
                        max_value = data_length_result['p'].loc[index_count - 1] 
                        break
                index_count += 1

            highest_data = data_length_result[data_length_result['p'] == max_value].copy()
            e_value = highest_data['a']

            # Checking the optimal values
            if len(highest_data) == 1:
                max_value_up = max_value + 0.05
                data_length_result = data_length_result[
                    (data_length_result['p'] <= max_value_up) & (data_length_result['p'] >= max_value)].copy()
                min_error = data_length_result['sum_error'].min()
                e_value = data_length_result[data_length_result['sum_error'] == min_error]['a']
                b = data_length_result[data_length_result['sum_error'] == min_error]['b']
                b_F = b.values[0]
                a_F = e_value.values[0]
                cof = [a_F, b_F]
                return cof

            else:
                result_matrix = pd.DataFrame({'kT': kT_values, 'sum_error': diff_sum,
                                              'a': a_values, 'b': b_values})

                result_matrix = result_matrix[result_matrix['sum_error'] > 0].copy()
                result_matrix = result_matrix[result_matrix['a'].isin(e_value.values)]
                min_error = result_matrix['sum_error'].min()
                e_value = result_matrix[result_matrix['sum_error'] == min_error]['a']
                b_v = result_matrix[result_matrix['sum_error'] == min_error]['b']
                a_F = e_value.values[0]
                b_F = b_v.values[0]
                cof = [a_F, b_F]
                return cof

        def linear_fit_r2(data_frame):
            """
            A method that returns covariance matrix, r2, slope and the intercept
            :param data_frame: DataFrame with values to calculate.
            :return: r2, a, b, u(a)
            """
            results = data_frame.copy()

            lin_cof, cov_matrix = np.polyfit(data_frame['1/kT'], data_frame['ln(I)'], 1, cov=True)
            cov = np.sqrt(cov_matrix[0][0])

            linear_equation = np.poly1d(lin_cof)
            fitted_linear = [linear_equation(t) for t in data_frame['1/kT']]
            results['fitted'] = fitted_linear

            RSS = np.sum(np.square(results['ln(I)'] - results['fitted']))
            TSS = np.sum(np.square(results['ln(I)'] - results['fitted'].mean()))

            r2 = 1 - RSS / TSS
            return r2, lin_cof[0], lin_cof[1], cov

        # Finding blind coefficient for fitting function
        cof_blind = blind_fit(mean_points_chosen)
        a_blind, b_blind = cof_blind[0], cof_blind[1]
        fitted_blind = [linear_function(x, -a_blind, b_blind) for x in mean_points_chosen['1/kT']]

        data_frame_fitted_blind = pd.DataFrame(
            {'1/kT': mean_points_chosen['1/kT'], 'ln(I)': mean_points_chosen['ln(I)'], 'fitted_blind': fitted_blind})
        data_frame_fitted_blind = data_frame_fitted_blind[data_frame_fitted_blind['fitted_blind'] > 0].copy()
        data_frame_fitted_blind['perc'] = data_frame_fitted_blind['fitted_blind'] / data_frame_fitted_blind[
            'ln(I)'] * 100
        data_frame_chosen_from_blind = data_frame_fitted_blind[data_frame_fitted_blind['perc'] >= 90].copy()

        if len(data_frame_chosen_from_blind) > 2:
            r2_chosen, a_chosen, b_chosen, uncertain_a = linear_fit_r2(data_frame_chosen_from_blind)

            a_mean = (a_chosen + (-a_blind)) / 2
            b_mean = (b_chosen + b_blind) / 2
            fitted_mean = [linear_function(x, a_mean, b_mean) for x in data_frame_chosen_from_blind['1/kT']]
            x_line = data_frame_chosen_from_blind

        else:
            r2_chosen, a_chosen, b_chosen, uncertain_a = linear_fit_r2(data_frame_fitted_blind)
            a_mean = (a_chosen + (-a_blind)) / 2
            b_mean = (b_chosen + b_blind) / 2
            fitted_mean = [linear_function(x, a_mean, b_mean) for x in data_frame_fitted_blind['1/kT']]
            x_line = data_frame_fitted_blind

        self.a_uncertain = uncertain_a
        self.e = - a_mean
        self.x_line = x_line
        self.y_line = fitted_mean
