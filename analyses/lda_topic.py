def fix_lda_model(dir_name, corpus, no_below, no_above, num_topics=15, base_path='../../cache'):
    dictionary = Dictionary(corpus)
    dictionary.filter_extremes(no_below=no_below, no_above=no_above)
    dictionary.save(os.path.join(base_path, 'lda', dir_name + ".dic"))
    corpus_vec = [dictionary.doc2bow(tokens) for tokens in corpus]

    lda = LdaModel(corpus_vec, num_topics=num_topics, id2word=dictionary)
    lda.save('models/lda/' + str(leg_period) + 'th_leg_period.model')
    return lda, corpus_vec


def get_topic_for_speechs(lda, corpus_vec):
    topics_map = []
    for i, c in enumerate(datasets[1][0]):
        ts = sorted(lda.get_document_topics(corpus_vec[i]), key = lambda x: x[1], reverse=True)
        topics_map.append([c[0], c[1], ts[0][0], ts[0][1], beifall_indices[i], speech_indices[i]])
    topics_map = np.array(topics_map)
    return topics_map


def percentage_of_selected(selected_features, classes):
    selected_classes, selected_counts = np.unique(selected_features, return_counts=True)
    counts = [np.squeeze(selected_counts[selected_classes == c]) if c in selected_classes else 0\
              for c in classes]
    return counts / np.sum(counts)
