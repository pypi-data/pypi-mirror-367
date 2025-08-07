import sys
import os
import logging
# Configure logging
logger = logging.getLogger(__name__)

def coord2int(coordinate):
	"""
	Convert string coordinate to chr, start, and end.
	"""
	try:
		# Split by colon and dash
		chrom, pos = coordinate.split(":")
		# Add "chr" prefix if not present
		chrom = f"chr{chrom}" if not chrom.startswith("chr") and (chrom.isdigit() or chrom in ["X", "Y", "M", "MT"]) else chrom
		start, end = pos.split("-")
		# Convert to integer
		start = int(start)
		end = int(end)
	except:
		logger.error(f"Invalid coordinate format: {coordinate}")
		logger.error("Please provide a valid coordinate format: chr:start-end")
		raise ValueError(f"Invalid coordinate format: {coordinate}")
		sys.exit(1)
	return chrom, start, end

def posid2int(positional_id, shiba_path, extend_up, extend_down) -> tuple:
	"""
	Get chromosome, start, and end of the target region and junction coordinates from positional ID.
	"""
	# Parse event type from positional ID (i.e. SE@chr10@20327164-20327391@20326099-20328102)
	event_type = positional_id.split("@")[0] # (SE, FIVE, THREE, MXE, RI, AFE, ALE, MSE)
	# Get EVENT file path
	event_file_path = os.path.join(shiba_path, "events", f"EVENT_{event_type}.txt")
	# Check if EVENT file exists
	if not os.path.exists(event_file_path):
		logger.error(f"EVENT file not found: {event_file_path}")
		logger.error("Please double check and provide a valid positional ID")
		raise FileNotFoundError(f"EVENT file not found: {event_file_path}")
		sys.exit(1)
	# Read EVENT file
	event_file_col_dict = {}
	header_dict = {}
	with open(event_file_path, "r") as event_file:
		for line in event_file:
			line = line.strip()
			# Skip header
			if line.startswith("event_id"):
				header = line.split("\t")
				for i, col in enumerate(header):
					header_dict[col] = i
				continue
			# Store values in dictionary if the 2nd column matches positional ID
			pos_id_col = line.split("\t")[1]
			if pos_id_col == positional_id:
				# Get all columns and store in dictionary
				columns = line.split("\t")
				for col, i in header_dict.items():
					try:
						event_file_col_dict[col] = columns[i]
					except:
						event_file_col_dict[col] = None
				break
	# Check if positional ID exists in EVENT file
	if not event_file_col_dict:
		logger.error(f"Positional ID not found in EVENT file: {positional_id}")
		logger.error("Please double check and provide a valid positional ID")
		raise ValueError(f"Positional ID not found in EVENT file: {positional_id}")
		sys.exit(1)
	# Get chromosome, start, and end from positional ID
	chrom = positional_id.split("@")[1]
	# Add "chr" prefix if not present
	chrom = f"chr{chrom}" if not chrom.startswith("chr") and (chrom.isdigit() or chrom in ["X", "Y", "M", "MT"]) else chrom
	# Get strand from EVENT file
	strand = event_file_col_dict["strand"]
	# Get gene name from EVENT file
	gene_name = event_file_col_dict["gene_name"]
	# Extend upstream and downstream
	intron_key_map = {
		"SE": "intron_c",
		"FIVE": "intron_b",
		"THREE": "intron_b",
		"MXE": ["intron_a1", "intron_a2"],
		"RI": "intron_a",
		"AFE": "intron_a",
		"ALE": "intron_a",
		"MSE": "intron"
	}
	if event_type in intron_key_map:
		intron_keys = intron_key_map[event_type]
		if isinstance(intron_keys, list):
			start = int(event_file_col_dict[intron_keys[0]].split(":")[1].split("-")[0]) - extend_down
			end = int(event_file_col_dict[intron_keys[1]].split(":")[1].split("-")[1]) + extend_up
		else:
			intron = event_file_col_dict[intron_keys]
			if event_type == "AFE":
				start = int(intron.split(";")[0].split(":")[1].split("-")[0]) - extend_up if strand == "+" else int(intron.split(";")[-1].split(":")[1].split("-")[0]) - extend_down
				end = int(intron.split(";")[-1].split(":")[1].split("-")[1]) + extend_down if strand == "+" else int(intron.split(";")[0].split(":")[1].split("-")[1]) + extend_up
			elif event_type == "ALE":
				start = int(intron.split(";")[-1].split(":")[1].split("-")[0]) - extend_up if strand == "+" else int(intron.split(";")[0].split(":")[1].split("-")[0]) - extend_down
				end = int(intron.split(";")[0].split(":")[1].split("-")[1]) + extend_down if strand == "+" else int(intron.split(";")[-1].split(":")[1].split("-")[1]) + extend_up
			else:
				if event_type == "MSE":
					intron = intron.split(";")[-1]
				start = int(intron.split(":")[1].split("-")[0]) - extend_up if strand == "+" else int(intron.split(":")[1].split("-")[0]) - extend_down
				end = int(intron.split(":")[1].split("-")[1]) + extend_down if strand == "+" else int(intron.split(":")[1].split("-")[1]) + extend_up
		if start < 0:
			start = 0
	else:
		logger.error(f"Unsupported event type: {event_type}")
		logger.error("Please provide a valid positional ID with supported event type")
		raise ValueError(f"Unsupported event type: {event_type}")
		sys.exit(1)

	# Get junction coordinates
	junction_list = []
	junction_direction_dict = {}
	junction_key_map = {
		"SE": {"up": ["intron_c"], "down": ["intron_a", "intron_b"]},
		"FIVE": {"up": ["intron_b"], "down": ["intron_a"]},
		"THREE": {"up": ["intron_b"], "down": ["intron_a"]},
		"MXE": {"up": ["intron_b1", "intron_b2"], "down": ["intron_a1", "intron_a2"]},
		"RI": "intron_a",
		"AFE": {"up": ["intron_a"], "down": ["intron_b"]},
		"ALE": {"up": ["intron_a"], "down": ["intron_b"]},
		"MSE": "intron"
	}
	junction_keys = junction_key_map[event_type]
	if event_type == "MSE":
		for i, j in enumerate(event_file_col_dict[junction_keys].split(";")):
			if i == len(event_file_col_dict[junction_keys].split(";")) - 1:
				junction_list += [j]
				junction_direction_dict[j] = "up"
			else:
				junction_list += [j]
				junction_direction_dict[j] = "down"
	elif event_type == "RI":
		junction_list += [event_file_col_dict[junction_keys]]
		junction_direction_dict[event_file_col_dict[junction_keys]] = "up"
	else:
		for direction in ["up", "down"]:
			for key in junction_keys[direction]:
				for junction in event_file_col_dict[key].split(";"):
					junction_list += [junction]
					junction_direction_dict[junction] = direction
	return chrom, start, end, strand, gene_name, junction_list, junction_direction_dict
