#!/usr/bin/env python3
import os
import re
from collections import defaultdict
import traceback

# This is to read and return the content of a file.
def read_file(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File `{file_path}` doesn't exist")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def read_values(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File `{file_path}` doesn't exist")
    with open(file_path, "r", encoding="utf-8") as f:
        return {line.split()[0]: line.split()[1] for line in f}

def txt_abbrevs(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File `{file_path}` doesn't exist")
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f]

def process_words(word_list):
    return [re.sub(r'[^A-Za-z]+', ' ', word.upper().replace("'", "")) for word in word_list]

# joins processed words by removing spaces.
def join_words(word_list):
    return [''.join(entry.split()) for entry in word_list]

# to generate abbreviations for the list of processed words and handling duplicates.
def gen_abbrevs(word_list):
    abbrevs_dict = {}
    duplicates = set()

    for entry in word_list:
        abbrevs_set = set(generate_abbreviations(entry))
        duplicates.update(abbrevs_set.intersection(*abbrevs_dict.values()))
        abbrevs_dict[entry] = list(abbrevs_set)

    return remove_duplicates_from_dict(duplicates, abbrevs_dict)

def generate_abbreviations(word):
    return [word[0] + word[i] + word[j] for i in range(1, len(word)) for j in 
            range(i+1, len(word)) if ' ' not in word[0] + word[i] + word[j]]

def remove_duplicates_from_dict(duplicates, abbreviations_dict):
    for duplicate_entry in duplicates:
        for value in abbreviations_dict.values():
            if duplicate_entry in value:
                value.remove(duplicate_entry)
    return abbreviations_dict

def wordindex(input_string):
    char_map = defaultdict(list)
    accumulator = 0

    for char in input_string:
        if char == input_string[0]:
            accumulator = 0
        elif char == ' ':
            accumulator = -1
        elif input_string[-1] == char:
            accumulator = -1
        else:
            accumulator += 1

        if char != ' ':
            char_map[char].append(accumulator)

    return char_map

def getAbbreviationIndex(result, abbreviation):
    abbreviation_indexes = []
    current_positions = {char: 0 for char in abbreviation}

    for char in abbreviation:
        if char in result:
            char_indexes = result[char]
            if char_indexes:
                index = char_indexes[current_positions[char]]
                abbreviation_indexes.append(index)
                current_positions[char] += 1

    return abbreviation_indexes

# to calculate the score of the abbreviation
def score_abbreviation(score_card, abbrevs_dict):
    final_score = {}
    position_scores = {0: 0, -1: 5, 1: 1, 2: 2}
    letter_scores = {letter: score for letter, score in score_card.items()}

    for word, abbreviations in abbrevs_dict.items():
        word_scores = {}

        for abbreviation in abbreviations:
            abbreviation = abbreviation.upper()
            word = word.upper()

            indexes = wordindex(word)
            abbreviationIndexes = getAbbreviationIndex(indexes, abbreviation)

            first_score = 0
            second_score = int(position_scores.get(abbreviationIndexes[1], 0)) + int(letter_scores.get(abbreviation[1], 0))
            third_score = int(position_scores.get(abbreviationIndexes[2], 0)) + int(letter_scores.get(abbreviation[2], 0))
            total_score = first_score + second_score + third_score
            word_scores[abbreviation] = total_score

        final_score[word] = word_scores

    return final_score

def assign_entries_to_dict_keys(entry_list, target_dict):
    assigned_dict = {}

    for i, entry in enumerate(entry_list):
        if i < len(target_dict):
            key = list(target_dict.keys())[i]
            assigned_dict[key] = entry
        else:
            print(f"Not enough keys in the dictionary for entry: {entry}")

    return assigned_dict

def main():
    file_name = input("Enter the name of the file to read: ")

    try:
        # Read values and abbreviations from files
        value_score = read_values("values.txt")
        abb_file = txt_abbrevs(file_name)

        # Process words and generate abbreviations
        processed_abb_file = process_words(abb_file)
        abbrevs_dict = gen_abbrevs(processed_abb_file) #duplicates

        # Remove duplicates from abbreviations
        # result_dict = remove_duplicates_from_dict(duplicates, abbrevs_dict)

        # Score abbreviations
        scores = score_abbreviation(value_score, abbrevs_dict) #result_dict

        # Write output to file
        output_file = f"Chrisidisi_{str(file_name.split('.')[0])}_abbrevs.txt"
        with open(output_file, 'w') as output_file:
            for word, word_scores in scores.items():
                output_file.write(word + ":\n")
                for abbreviation, score in word_scores.items():
                    output_file.write(f"  {abbreviation}\n")
                output_file.write("\n")

        print(f"Output written to {output_file}")

    except Exception as e:
        traceback.print_exc()
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
