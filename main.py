import os
import pandas as pd
import numpy as np

from preprocess.parse_party import parse_party
from preprocess.preprocess import preprocess
from parser.parse_new_protocol import parse_new_protocol
from parser.parse_old_protocol import parse_old_protocol
from parser.parse import parse_protocols



np_preprocess = np.vectorize(preprocess)
np_parse_party = np.vectorize(parse_party)

def contain_beifall(text):
    return 'beifall' in text

np_contain_beifall = np.vectorize(contain_beifall)

def contain_speech(text):
    return 'speech' in text

np_contain_speech = np.vectorize(contain_speech)

def get_data(dir_name, base_path='../.cache'):
    data_path = os.path.join(base_path, 'data', dir_name)
    header = ['session', 'segment', 'speaker', 'speech', 'comment']

    parsed_path = os.path.join(base_path, 'parsed_data', dir_name + '.csv')
    if not os.path.exists(parsed_path):
        parse_protocol = parse_new_protocol if dir_name == 'pp19-data' else parse_old_protocol
        paragraphs = parse_protocols(data_path, parse_protocol)
        save_csv(parsed_path, header, paragraphs)
    df_parsed = pd.read_csv(parsed_path, na_filter=False)
    data_parsed = df_parsed.values.copy()

    preprocessed_path = os.path.join(base_path, 'preprocessed_data', dir_name + '.csv')
    if not os.path.exists(preprocessed_path):
        data_parsed[:, 2] = np_parse_party(data_parsed[:, 2])
        data_parsed[:, 3] = np_preprocess(data_parsed[:, 3])
        save_csv(preprocessed_path, header, data_parsed)
    df_preprocessed = pd.read_csv(preprocessed_path, na_filter=False)
    data_preprocessed = df_preprocessed.values.copy()

    categorized_path = os.path.join(base_path, 'categorized_comment', dir_name + '.csv')
    if not os.path.exists(categorized_path):
        comments = [parse_comment(row[4]) for row in data_preprocessed]
        save_csv(categorized_path, parties, comments)
    df_categorized_comments = pd.read_csv(categorized_path, na_filter=False)
    data_categorized_comments = df_categorized_comments.values.copy()

    corpus = [t.split() for t in data_preprocessed[:, 3]]
    return data_preprocessed, corpus, data_categorized_comments

def get_plots(dataset, parties, title_when, lda, corpus_vec, party_indices=True):
    speaker = dataset[0][:, 2]
    np_parties = np.array(parties)

    party_indices = party_indices * (np_parties != 'alterspräsident') * \
            (np_parties != 'vizepräsident') * (np_parties != 'präsident')

    selected_parties = np_parties[party_indices]
    comments = dataset[2][:, party_indices]

    beifall_comments = np_contain_beifall(comments)
    speech_comments = np_contain_speech(comments)
    beifall_indices = np.sum(beifall_comments, axis=1) > 0
    speech_indices = np.sum(speech_comments, axis=1) > 0

    when_str = " in " + str(title_when) + "th Legislative Period"
    # categorize comment
    x_comment, y_comment = get_response_counts(comments)
    draw_bar_chart(x_comment, y_comment, x_label='Types', y_label="Count",
               title="Types of Response" + when_str,
               filename="Response" + str(title_when))

    # analysis speaker
    x_speaker, y_speaker = np.unique(speaker, return_counts=True)
    x_speaker, y_speaker = sorted_topn(x_speaker, y_speaker)
    draw_bar_chart(x_speaker, y_speaker, x_label='Parties', y_label='Count',
                   title="Parties of Speakers" + when_str,
                   filename="Speakers" + str(title_when))

    # analysis comment
    x_all_comment, y_all_comment = get_party_sepcified_reaction_counts(selected_parties, comments != '')
    draw_bar_chart(x_all_comment, y_all_comment, x_label='Parties', y_label="Count",
               title="Interjection of Parties" + when_str,
               filename="ResponseOfParties" + str(title_when))


    x_beifall_comment, y_beifall_comment = get_party_sepcified_reaction_counts(selected_parties, beifall_comments)
    draw_bar_chart(x_beifall_comment, y_beifall_comment, x_label='Parties', y_label="Count",
               title="Beifall in Interjection of Parties" + when_str,
               filename="BeifallOfParties" + str(title_when))

    x_speech_comment, y_speech_comment = get_party_sepcified_reaction_counts(selected_parties, speech_comments)
    draw_bar_chart(x_speech_comment, y_speech_comment, x_label='Parties', y_label="Count",
               title="Speech in Interjection of Parties" + when_str,
               filename="SpeechOfParties" + str(title_when))

    # analysis speaker
    Y_beifall = get_comment_for_speaker(selected_parties, speaker, beifall_comments)
    draw_multibar_chart(selected_parties, Y_beifall,
                        x_label="The Response Come from Party",
                        y_label="Number of Beifall in Interjection",
                        filename="BeifallOfEachPartyToEachParty" + str(title_when))

    Y_speech = get_comment_for_speaker(selected_parties, speaker, speech_comments)
    draw_multibar_chart(selected_parties, Y_speech,
                        x_label="The Response Come from Party",
                        y_label="Number of Speech in Interjection",
                        filename="SpeechOfEachPartyToEachParty" + str(title_when))


    topics_map = get_topic_for_speech(lda, corpus_vec)
    classes = np.unique(topics_map[:, 2])

    positive_percentage = percentage_of_selected(topics_map[beifall_indices, 2], classes)
    negative_percentage = percentage_of_selected(topics_map[~beifall_indices, 2], classes)
    Y = np.array([positive_percentage, negative_percentage])
    draw_multibar_chartx(['beifall', 'not beifall'], Y, \
                    x_label='topic id', y_label='number', filename="BeifallTopics19")

    positive_percentage = percentage_of_selected(topics_map[indices, 2], classes)
    negative_percentage = percentage_of_selected(topics_map[~indices, 2], classes)
    Y = np.array([positive_percentage, negative_percentage])
    draw_multibar_chartx(['speech', 'not speech'], Y, \
                    x_label='topic id', y_label='number', filename="SpeechTopics19")

