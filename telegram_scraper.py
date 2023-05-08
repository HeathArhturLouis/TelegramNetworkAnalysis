from telethon.sync import TelegramClient
import telethon.sync
import pandas as pd
import asyncio

from datetime import timedelta
import datetime
import pytz

import os

from tqdm.asyncio import tqdm as atqdm

# Helper function for getting the first and last message in a date ranges


async def fetch_bounds(client, channel, from_date, to_date, verbose=False):
    # Get ID of oldest message in range via offset parameters

    pre_first_msg = await client.get_messages(channel, offset_date=from_date, limit=1)

    ######
    full_history = False

    if len(pre_first_msg) == 0:
        # We want the entire chat history going back
        min_id = 0
    else:
        pre_first_msg = pre_first_msg[0]

        first_msg = await client.get_messages(
            channel, min_id=pre_first_msg.id, limit=1, reverse=True
        )

        if len(first_msg) == 0:
            min_id = 0
        else:
            first_msg = first_msg[0]
            min_id = first_msg.id

    # Get ID of youngest message in range via offset parameters

    last_msg = await client.get_messages(channel, offset_date=to_date, limit=1)

    if len(last_msg) == 0:
        # No messages in whole range
        return None
    else:
        last_msg = last_msg[0]
        max_id = last_msg.id

    return [min_id, max_id]


async def process_messages_in_time_range(
    client, chat, from_date, to_date, function=lambda x: print(x.text), limit=None
):
    bounds = await fetch_bounds(client, chat, from_date, to_date)

    if bounds == None:
        # Nothing in bounds
        return

    async for message in client.iter_messages(
        chat, min_id=bounds[0], max_id=bounds[1], limit=limit
    ):
        if message.text == None:
            continue
        function(message)


def construct_interval(from_date, to_date, sample_delta, no_samples):
    """
    sample_delta:
    Datetime timedelta as in delta = timedelta(minutes=5)
    determines length of individual interval

    no_samples:
    number of points to sample
    """

    # Length of time between intervals

    interval_delta = (to_date - from_date) / no_samples

    offset = from_date
    intervals = []

    for i in range(no_samples):
        intervals.append([offset, offset + sample_delta])
        offset += interval_delta

    return intervals


async def process_samples_multi_interval(client, chat, intervals, function, limit=None):
    for interval in intervals:
        fd = interval[0]
        td = interval[1]
        await process_messages_in_time_range(
            client, chat, from_date=fd, to_date=td, function=function, limit=limit
        )


def message_csv_line_write_factory(file):
    """
    As a side effect strips newlines and commas
    """
    return lambda msg: file.write(
        str(msg.id)
        + ","
        + str(msg.sender_id)
        + ","
        + str(msg.date)
        + ","
        + (msg.text).replace("\n", " ").replace(",", " ")
        + "\n"
    )


async def scrape_data(
    client, chats, epochs, sample_delta, no_samples, data_path, verbose=True
):
    counter = 0
    operations = len(epochs) * len(chats)

    for epoch_name in epochs.keys():
        epoch_intervals = construct_interval(
            from_date=epochs[epoch_name][0],
            to_date=epochs[epoch_name][1],
            sample_delta=sample_delta,
            no_samples=no_samples,
        )

        for chat in chats:
            counter += 1
            if verbose:
                print(
                    "data for ",
                    chat,
                    " on epoch ",
                    str(epochs[epoch_name][0]),
                    " -- ",
                    str(epochs[epoch_name][1]),
                    f". Operation: {counter} / {operations}",
                )

            f_name = os.path.join(data_path, f"chat_{chat}_epoch_{epoch_name}.csv")

            with open(f_name, "w") as file:
                # Header
                file.write("MessageID,SenderID,MessageDate,MessageText\n")
                function = message_csv_line_write_factory(file)

                await process_samples_multi_interval(
                    client, chat, epoch_intervals, function, limit=None
                )
