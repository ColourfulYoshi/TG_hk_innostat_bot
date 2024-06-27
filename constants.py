URLS = {
	"detailed": "https://bot.innoprog.ru/dataset/detailed/<ID>",
	"general": "https://bot.innoprog.ru/dataset/general/<ID>",
	"task": "https://api.innoprog.ru:3000/task/<ID>"
}

def get_url(name, endpoint_id):
	return URLS.get(name, "NONE").replace("<ID>", endpoint_id)

def divide_time_string(time_str: str):
	return {
		"day": int(time_str.split(" ")[0].split("-")[0]),
		"month": int(time_str.split(" ")[0].split("-")[1]),
		"year": int(time_str.split(" ")[0].split("-")[2]),
		"hour": int(time_str.split(" ")[1].split(":")[0]),
		"minute": int(time_str.split(" ")[1].split(":")[1]),
		"second": int(time_str.split(" ")[1].split(":")[2]),
	}

def remove_letters(string: str):
	getVals = list([val for val in string if val.isalpha() or val.isnumeric()])
	result = "".join(getVals)
	return result

def get_average(li: list):
	if len(li) == 0:
		return 0
	return sum(li) / len(li)

def minute_add_end(minute: int):
	if str(minute)[-1:] in ["2", "3", "4"] and str(minute)[0] != "1":
		return "минуты"
	elif str(minute)[-1:] == "1":
		return "минута"
	else:
		return "минут"

def find_dicts_with_key(li: list, key: str, value: any):
	result = []
	for d in li:
		if d.get(key) == value:
			result.append(d)
	return result

def time_dict_to_seconds(d: {}):
	result = d["second"]
	result += d["minute"] * 60
	result += d["hour"] * 3600
	result += d["day"] * (3600 * 24)
	result += d["month"] * (3600 * 24 * 30)
	result += d["year"] * (3600 * 24 * 30 * 365)
	return result

def num_to_range(num, start_min, start_max, out_min, out_max):
	return out_min + (float(num - start_min) / float(start_max - start_min) * (out_max - out_min))
