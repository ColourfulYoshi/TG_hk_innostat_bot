NL = '\n'

import requests
import math
import random
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler
from telegram.constants import ParseMode

import constants

async def statistics_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
	try:
		user_id = str(context.args[0])
		prog_bar = 35
		g_data = requests.get(constants.get_url("general", user_id))
		d_data = requests.get(constants.get_url("detailed", user_id))
		if g_data.status_code == 200 and d_data.status_code == 200:
			status_message = await update.effective_chat.send_message(f"*{'=' * prog_bar}*\n\n📜 Получение информации о "
																	  f"`{user_id}`...\n\n*{'=' * prog_bar}*",
																	  parse_mode=ParseMode.MARKDOWN)
			general_json = g_data.json()
			detailed_json = d_data.json()
			result = f"""*📊 Статистика пользователя* `{user_id}`*:*\n
• 🧮 Общее количество решённых заданий: `<task_amount>`
• ⌛ Среднее время решения заданий: `<average_time>`
• 💯 Средняя оценка сложности от пользователя (реальные баллы): `<average_real_points>`
• 🆚 Среднее отклонение от оценки сложности преподавателя: `<average_point_difference>`
• ⏱️ Среднее время между попытками решения: `<average_time_between_attempts>`
• #️⃣ Среднее количество попыток для заданий:
   ‣ 🔘 С вариантами ответов: `<attempt_count_multichoice>`
   ‣ ❓ Открытый вопрос: `<attempt_count_open>`
   ‣ 👨‍💻 Написание кода: `<attempt_count_code>`
   ‣ 💾 Дополнение кода: `<attempt_count_codeedit>`
• ✨ Процент правильных ответов с первой попытки:
   ‣ 🔘 Для заданий с вариантами ответов: `<first_try_multichoice>%`
   ‣ ❓ Для заданий с открытым ответом: `<first_try_open>%`
   ‣ 👨‍💻 Для заданий с написанием кода: `<first_try_code>%`
   ‣ 💾 Для заданий с дополнением кода: `<first_try_codeedit>%`"""
			replacements = {
				"<task_amount>": 0,
				"<average_time>": [],
				"<average_real_points>": [],
				"<average_point_difference>": [],
				"<average_time_between_attempts>": [],
				"<attempt_count_multichoice>": [],
				"<attempt_count_open>": [],
				"<attempt_count_code>": [],
				"<attempt_count_codeedit>": [],
				"<first_try_multichoice>": [],
				"<first_try_open>": [],
				"<first_try_code>": [],
				"<first_try_codeedit>": []
			}
			corresponding_type_keys = {
				"С вариантами ответов": ["<attempt_count_multichoice>", "<first_try_multichoice>"],
				"Открытый вопрос": ["<attempt_count_open>", "<first_try_open>"],
				"Написание кода": ["<attempt_count_code>", "<first_try_code>"],
				"Дополнение кода": ["<attempt_count_codeedit>", "<first_try_codeedit>"]
			}
			matched = []
			last_update = 0
			for n, task in enumerate(general_json):
				if task.get("task_id") in matched:
					continue
				matched.append(task.get("task_id"))
				matching = constants.find_dicts_with_key(detailed_json, "task_id", task.get("task_id"))
				times = []
				for i in matching:
					times.append(constants.time_dict_to_seconds(constants.divide_time_string(i.get("time"))))
				times = sorted(times)
				average_time = 0
				if len(times) > 1:
					attempt_times = []
					for i in range(0, len(times)-1):
						attempt_times.append(abs(times[i+1] - times[i]) / 60)
					average_time = constants.get_average(attempt_times)
				else:
					average_time = float(constants.get_average(
						[int(constants.remove_letters(i)) for i in task.get("real_time").split("-")]
					))
				replacements["<average_time>"].append(average_time)
				replacements["<average_real_points>"].append(task.get("real_points"))
				replacements["<average_point_difference>"].append(task.get("real_points") - task.get("points"))
				replacements["<average_time_between_attempts>"].append(average_time / task.get("attempts"))
				
				t_data = requests.get(constants.get_url("task", str(task.get("task_id"))))
				if t_data.status_code != 200:
					if t_data.status_code == 404:
						await update.effective_chat.send_message(f"⚠️ Задание c *ID* `{task.get('task_id')}` "
																 f"больше не существует. Пропускаем.",
																 parse_mode=ParseMode.MARKDOWN)
					else:
						await update.effective_chat.send_message(f"⚠️ Ошибка при получении информации о задании "
																 f"`{task.get('task_id')}` со статусом "
																 f"`{t_data.status_code}`. Пропускаем.",
																 parse_mode=ParseMode.MARKDOWN)
				else:
					task_json = t_data.json()
					replacements[corresponding_type_keys.get(task_json.get("type"))[0]].append(task.get("attempts"))
					replacements[corresponding_type_keys.get(task_json.get("type"))[1]].append(1 if task.get("attempts") == 1 else 0)
				last_update -= 1
				if last_update <= 0 or n >= len(general_json)-1:
					last_update = random.randint(5, 9)
					percent = round(((n + 1) / len(general_json)) * 100)
					mapped = math.floor(constants.num_to_range(percent, 0, 100, 0, prog_bar))
					bar_string = f"*{'#' * mapped}{'=' * (prog_bar - mapped)}*"
					await status_message.edit_text(f"{bar_string}\n\n"
												   f"{status_message.text_markdown.split(NL)[2]}\n\n"
												   f"*[{percent}% "
												   f"({n + 1}/{len(general_json)})]* "
												   f"*ID* `{task.get('task_id')}`\n\n"
												   f"{bar_string}",
												   parse_mode=ParseMode.MARKDOWN)
			replacements["<task_amount>"] = str(len(matched))
			replacements["<average_time>"] = str(round(
				constants.get_average(replacements["<average_time>"])
			)) + " " + constants.minute_add_end(round(constants.get_average(replacements["<average_time>"])))
			replacements["<average_real_points>"] = round(
				constants.get_average(replacements["<average_real_points>"]), 1
			)
			replacements["<average_point_difference>"] = round(
				constants.get_average(replacements["<average_point_difference>"]), 1
			)
			replacements["<average_time_between_attempts>"] = str(round(
				constants.get_average(replacements["<average_time_between_attempts>"])
			)) + " " + constants.minute_add_end(round(constants.get_average(replacements["<average_time_between_attempts>"])))
			for k in corresponding_type_keys:
				task_type = corresponding_type_keys[k]
				replacements[task_type[0]] = str(round(constants.get_average(replacements[task_type[0]]), 1)) + \
										  f" (всего: {len(replacements[task_type[0]])})"
				replacements[task_type[1]] = str(round(constants.get_average(replacements[task_type[1]]) * 100, 1))
			for r in replacements:
				result = result.replace(r, str(replacements[r]))
			await update.effective_chat.send_message(result, parse_mode=ParseMode.MARKDOWN)
		else:
			if g_data.status_code == d_data.status_code == 404:
				await update.effective_chat.send_message(f"❌ Неверный `<user_id>`. Необходим айди пользоваьеля с сайта "
														 f"`innoprog.ru`.",
														 parse_mode=ParseMode.MARKDOWN)
			else:
				await update.effective_chat.send_message(f"❌ Ошибка при получении информации о пользователе.\n"
														 f"Статус код (общая информация): `{g_data.status_code}`\n"
														 f"Статус код (детализированная информация): `{d_data.status_code}`",
														 parse_mode=ParseMode.MARKDOWN)
	except (IndexError, ValueError) as e:
		await update.effective_chat.send_message("🌐 Использование: /statistics `<user_id>`\n",
												 parse_mode=ParseMode.MARKDOWN)

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
	cmds = {
		"start": [["help", "h"], "просмотр доступных комманд"],
		"statistics `<user_id>`": [["stats `<user_id>`", "st `<user_id>`"], "просмотр статистики пользователя"]
	}
	result = ""
	for k in cmds:
		cmd_variants = ""
		if len(cmds[k][0]) > 0:
			for i in cmds[k][0]:
				cmd_variants += f" | /{i}"
		result += f"/{k}{cmd_variants} - _{cmds[k][1]}_\n"
	await update.effective_chat.send_message(f"{'*=*' * 50}\n\n{result}\n{'*=*' * 50}", parse_mode=ParseMode.MARKDOWN)

COMMAND_LIST = {
	"start": [["help", "h"], help_cmd],
	"statistics": [["stats", "st"], statistics_cmd],
}
