def calculate_cost(file_path, search_term, cost_per_line):
    """
    Calculate the total cost based on the number of lines containing a specific search term.

    Parameters:
    file_path (str): The path to the file to be searched.
    search_term (str): The string to search for in each line of the file.
    cost_per_line (float): The cost per line that contains the search term.

    Returns:
    float: The total cost calculated.
    """
    try:
        # Initialize the counter for the number of lines containing the search term.
        line_count = 0

        with open(file_path, 'r') as file:
            for line in file:
                # Check if the search term is in the current line.
                if search_term in line:
                    line_count += 1

        total_cost = line_count * cost_per_line
        formatted_cost = "${:.2f}".format(total_cost)
        return formatted_cost

    except FileNotFoundError:
        return "The file was not found."
    except Exception as e:
        return f"An error occurred: {e}"


file_path_example = r'C:\Users\hyunj\OneDrive\Desktop\MVP\client.log'
search_term_example = 'upload'
cost_per_line_example = 0.20  # 10 cents per line

print(calculate_cost(file_path_example, search_term_example, cost_per_line_example))
