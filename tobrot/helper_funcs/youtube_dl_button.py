#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K | gautamjay52 | MaxxRider

import asyncio
import json
import logging
import math
import os
import shutil
import subprocess
import time
from datetime import datetime

import pyrogram
from tobrot import AUTH_CHANNEL, DOWNLOAD_LOCATION, LOGGER, GYTDL_COMMAND, HTTP_PROXY
from tobrot.helper_funcs.upload_to_tg import upload_to_gdrive, upload_to_tg


async def youtube_dl_call_back(bot, update):
    # LOGGER.info(update)
    cb_data = update.data
    get_cf_name = update.message.caption
    # LOGGER.info(get_cf_name)
    cf_name = ""
    if "|" in get_cf_name:
        cf_name = get_cf_name.split("|", maxsplit=1)[1]
        cf_name = cf_name.strip()
    # yt-dlp extractors
    tg_send_type, youtube_dl_format, youtube_dl_ext = cb_data.split("|")
    #
    current_user_id = update.message.reply_to_message.from_user.id
    current_touched_user_id = update.from_user.id
    if current_user_id != current_touched_user_id:
        await bot.answer_callback_query(
            callback_query_id=update.id,
            text="⚠️ Opps ⚠️ \n I Got a False Visitor 🚸 !! \n\n 📛 Stay At Your Limits !!📛",
            show_alert=True,
            cache_time=0,
        )
        return False, None

    user_working_dir = os.path.join(DOWNLOAD_LOCATION, str(current_user_id))
    # create download directory, if not exist
    if not os.path.isdir(user_working_dir):
        await bot.delete_messages(
            chat_id=update.message.chat.id,
            message_ids=[
                update.message.message_id,
                update.message.reply_to_message.message_id,
            ],
            revoke=True,
        )
        return
    save_ytdl_json_path = user_working_dir + "/" + str("ytdleech") + ".json"
    try:
        with open(save_ytdl_json_path, "r", encoding="utf8") as f:
            response_json = json.load(f)
        os.remove(save_ytdl_json_path)
    except (FileNotFoundError) as e:
        await bot.delete_messages(
            chat_id=update.message.chat.id,
            message_ids=[
                update.message.message_id,
                update.message.reply_to_message.message_id,
            ],
            revoke=True,
        )
        return False
    #
    response_json = response_json[0]
    # TODO: temporary limitations
    # LOGGER.info(response_json)
    #
    youtube_dl_url = response_json.get("webpage_url")
    LOGGER.info(youtube_dl_url)
    #
    custom_file_name = "%(title)s.%(ext)s"
    # https://superuser.com/a/994060
    LOGGER.info(custom_file_name)
    #
    await update.message.edit_caption(caption="**Trying To Download.... Please wait..**")

    tmp_directory_for_each_user = os.path.join(
        DOWNLOAD_LOCATION, str(update.message.message_id)
    )
    if not os.path.isdir(tmp_directory_for_each_user):
        os.makedirs(tmp_directory_for_each_user)
    download_directory = tmp_directory_for_each_user
    LOGGER.info(download_directory)
    download_directory = os.path.join(tmp_directory_for_each_user, custom_file_name)
    LOGGER.info(download_directory)
    command_to_exec = []
    # to keep default thumbnail of video which has its thumbnail
    thumb_image = None
    thumb_image = response_json.get("thumbnail", thumb_image)
    if tg_send_type == "audio":
        command_to_exec = [
            "yt-dlp",
            "-c",
            "--prefer-ffmpeg",
            "--extract-audio",
            "--audio-format",
            youtube_dl_ext,
            "--audio-quality",
            youtube_dl_format,
            youtube_dl_url,
            "-o",
            download_directory,
        ]
    else:
        for for_mat in response_json["formats"]:
            format_id = for_mat.get("format_id")
            if format_id == youtube_dl_format:
                acodec = for_mat.get("acodec")
                if acodec == "none":
                    youtube_dl_format += "+bestaudio"
                break

        command_to_exec = [
            "yt-dlp",
            "-c",
            "--embed-subs",
            "-f",
            youtube_dl_format,
            "--hls-prefer-ffmpeg",
            youtube_dl_url,
            "-o",
            download_directory,
        ]
    #
    command_to_exec.append("--no-warnings")
    # command_to_exec.append("--quiet")
    command_to_exec.append("--restrict-filenames")
    #
    if HTTP_PROXY != "":
        command_to_exec.append("--proxy")
        command_to_exec.append(HTTP_PROXY)
    if "contentx.me" in youtube_dl_url:
        command_to_exec.append("--referer")
        command_to_exec.append("https://contentx.me/")
    if "mail.ru" in youtube_dl_url:
        command_to_exec.append("--referer")
        command_to_exec.append("https://my.mail.ru/")
    if "molystream" in youtube_dl_url:
        command_to_exec.append("--referer")
        command_to_exec.append("https://dbx.molystream.org/")
    if "moly.cloud" in youtube_dl_url:
        command_to_exec.append("--referer")
        command_to_exec.append("https://vidmoly.to/")
    if "vh4nx.xyz" in youtube_dl_url:
        command_to_exec.append("--referer")
        command_to_exec.append("https://vh4nx.xyz/")
    if "closeload" in youtube_dl_url:
        command_to_exec.append("--referer")
        command_to_exec.append("https://closeload.com/")
    if "streammovie" in youtube_dl_url:
        command_to_exec.append("--referer")
        command_to_exec.append("https://streammovie.club/")
    if "cdnhan" in youtube_dl_url:
        command_to_exec.append("--referer")
        command_to_exec.append("https://d4msg.xyz/")
    if "hotstar" in youtube_dl_url:
        command_to_exec.append("--geo-bypass-country")
        command_to_exec.append("IN")
    LOGGER.info(command_to_exec)
    process = await asyncio.create_subprocess_exec(
        *command_to_exec,
        # stdout must a pipe to be accessible as process.stdout
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    # LOGGER.info(e_response)
    # LOGGER.info(t_response)
    ad_string_to_replace = "please report this issue on https://github.com/yt-dlp/yt-dlp"
    if e_response and ad_string_to_replace in e_response:
        error_message = e_response.replace(ad_string_to_replace, "")
        await update.message.edit_caption(caption=error_message)
        return False, None
    if t_response:
        dir_contents = len(os.listdir(tmp_directory_for_each_user))
        await update.message.edit_caption(caption=f"found {dir_contents} files")
        user_id = update.from_user.id
        #
        LOGGER.info(tmp_directory_for_each_user)
        for a, _, c in os.walk(tmp_directory_for_each_user):
            for d in c:
                e = os.path.join(a, d)
                gaut_am = os.path.basename(e)
                fi_le = e
                if cf_name:
                    fi_le = os.path.join(a, cf_name)
                    os.rename(e, fi_le)
                    gaut_am = os.path.basename(fi_le)

        is_cloud = False
        comd = update.message.reply_to_message.text
        LOGGER.info(comd)
        user_command = comd.split()[0]
        if user_command == "/" + GYTDL_COMMAND:
            is_cloud = True
        if is_cloud:
            shutil.move(fi_le, "./")
            final_response = await upload_to_gdrive(
                gaut_am, update.message, update.message.reply_to_message, user_id
            )
        else:
            final_response = await upload_to_tg(
                update.message,
                tmp_directory_for_each_user,
                user_id,
                {},
                bot,
                True,
                yt_thumb=thumb_image,
            )
        LOGGER.info(final_response)
        #
        try:
            shutil.rmtree(tmp_directory_for_each_user)
        except:
            pass
        #
    
