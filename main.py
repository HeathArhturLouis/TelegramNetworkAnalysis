import sys
import os

# Project imports
import config

from telethon import TelegramClient
import asyncio


import process_text
import telegram_scraper
import generate_graphs
import train_model


def save_graphs(ch_names):
    adjacency_matrixes = generate_graphs.generate_url_and_user_nw(
        config.epochs, ch_names, config.raw_data_path
    )

    for epoch_name in config.epochs.keys():
        # Construct URL Graph
        generate_graphs.construct_graph(
            adjacency_matrixes["URL"][epoch_name],
            ch_names,
            epoch_name,  # Name of the epoch
            config.epochs,
            config.sample_delta,  # Interval of each sample
            config.no_samples,  # number of equally spaced samples to use
            "URL",  # Type of graph, should be one of URL, UserID or Topic
            config.graph_data_path,  # Directory where to store graph data
        )

        # Construct User Graph
        generate_graphs.construct_graph(
            adjacency_matrixes["UserID"][epoch_name],
            ch_names,
            epoch_name,  # Name of the epoch
            config.epochs,
            config.sample_delta,  # Interval of each sample
            config.no_samples,  # number of equally spaced samples to use
            "UserID",  # Type of graph, should be one of URL, UserID or Topic
            config.graph_data_path,  # Directory where to store graph data
        )


async def scrape_data(ch_names):
    print("Scraping Data:")

    # ---- CONNECT AND AUTHENTICATE ----
    print("1/3 - Connecting to Telethon Client")
    client = TelegramClient(
        None, config.credentials["api_id"], config.credentials["api_hash"]
    )
    await client.start()

    # ---- SCRAPE AND SAVE DATA
    print("2/3 - Scraping and Saving Data")

    # Call Data Scraper
    await telegram_scraper.scrape_data(
        client=client,
        chats=ch_names,
        epochs=config.epochs,
        sample_delta=config.sample_delta,
        no_samples=config.no_samples,
        data_path=config.raw_data_path,
        verbose=True,
    )

    # ---- END SESSION ----
    print("3/3 - Ending Telethon Session")
    await client.log_out()


def preprocessing(ch_names):
    fnames = process_text.construct_fnames(
        config.epochs, ch_names, config.raw_data_path
    )
    assert process_text.check_fnames(fnames)

    process_text.concatenate_csv_files(
        fnames, os.path.join(config.raw_data_path, "_all.csv")
    )


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Usage
        print(
            """Usage (Should be run sequentially):
        main.py -s [channel_file_name] <---- Scrape data and populate (overwrite) raw data folder
        main.py -p [channel_file_name] <---- Preprocess scraped data and prepare it for training
        main.py -g [channel_file_name] <---- Generate and save URL and UserID graph files
        main.py -t [model_type] [model_name] <---- Train model of selected type and save it to [model_name]. Currently supports [tSVD]


        main.py --test [Type] [Epoch] <---- Display the specified graph in a very ugly matplotlib plot. Type is one of 'URL', 'UserID' and 'Topics'
        """
        )
        quit()

    if sys.argv[1] == "--test":
        graph_file = os.path.join(
            config.graph_data_path, f"{sys.argv[2]}_graph_{sys.argv[3]}.graphml"
        )
        generate_graphs.plot_graphml(graph_file)
        quit()

    if sys.argv[1] == "-t":
        if sys.argv[2] == "tSVD":
            mdl = train_model.train_SVD_model(
                os.path.join(config.raw_data_path, "_all.csv"), verbose=True
            )
            train_model.save_topic_model(mdl, sys.argv[3])
        else:
            print("Please specify supported model type")
        quit()

    with open(os.path.join(config.chat_data_path, sys.argv[2]), "r") as file:
        # Discard cname
        file.readline()
        ch_names = [name.rstrip() for name in file]

    if sys.argv[1] == "-s":
        asyncio.run(scrape_data(ch_names))

    if sys.argv[1] == "-p":
        print("Preprocessing Data")
        preprocessing(ch_names)

    if sys.argv[1] == "-g":
        print("Generating and Storing Graphs")
        save_graphs(ch_names)
