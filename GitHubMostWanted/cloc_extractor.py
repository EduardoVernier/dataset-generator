import csv
import timeit
import os
import optparse


# Single repository usage:
# python2 cloc_extractor.py -f /home/eduardo/Desktop/tinyspline -m
if __name__ == "__main__":

	parser = optparse.OptionParser("usage: %prog [-f ./example_dir] [-a/-d/-m/-y] [-b master (optional)]")

	parser.add_option("-f", "--folder", dest="folder", type="string",
					  help="specify directory with downloaded repositories")

	parser.add_option("-b", "--branch", dest="branch",
					  default="master", type="string",
					  help="specify branch to run analisys on -- default = master")

	parser.add_option('-a', '--all', action='store_true', dest='all',
					  default=False, help="collect loc data for all commits")
	parser.add_option('-d', '--daily', action='store_true', dest='daily',
					  default=False, help="collect loc data for one commit a day")
	parser.add_option('-m', '--monthly', action='store_true', dest='monthly',
					  default=False, help="collect loc data for one commit a month")
	parser.add_option('-y', '--yearly', action='store_true', dest='yearly',
					  default=False, help="collect loc data for one commit a year")

	options, args = parser.parse_args()


	if not ((options.all ^ options.daily) ^ (options.monthly ^ options.yearly)):
		parser.print_help()
	else:
		# To run extraction, paste of copy of this file on the git repo folder and run "python extractor.py"
		# os.popen("mkdir output")
		period = ''
		if (options.all):
			period = '-a'
		elif (options.daily):
			period = '-d'
		elif (options.monthly):
			period = '-m'
		elif (options.yearly):
			period = '-y'

		output_dir = os.getcwd() + '/output/gh-' + options.folder.split('/')[-1] + period + '/'
		os.chdir(options.folder)
		print output_dir

		if (options.all):
			commits =  os.popen("git log " + options.branch + " --pretty=format:\"%cd %H\" --date=format:\'%Y %m %d\' | sort -nr | uniq -c | sed -e \'s/^ *\\([0-9]\\+\\) \\(.\\+\\)/\\2 \\1/\'").read().split("\n")
		elif (options.daily):
			commits =  os.popen("git log " + options.branch + " --pretty=format:\"%cd %H\" --date=format:\'%Y %m %d\' | awk \'{ if (y!=$1 || m!=$2 || d!=$3) { y=$1; m=$2; d=$3; last=$0; print $0 } else  { print last }}\' | sort -nr | uniq -c | sed -e \'s/^ *\\([0-9]\\+\\) \\(.\\+\\)/\\2 \\1/\'").read().split("\n")
		elif (options.monthly):
			commits = os.popen("git log " + options.branch + " --pretty=format:\"%cd %H\" --date=format:\'%Y %m %d\' | awk \'{ if (y!=$1 || m!=$2) { y=$1; m=$2; last=$0; print $0 } else  { print last }}\' | sort -nr | uniq -c | sed -e \'s/^ *\\([0-9]\\+\\) \\(.\\+\\)/\\2 \\1/\'").read().split("\n")
		elif (options.yearly):
			commits = os.popen("git log " + options.branch + " --pretty=format:\"%cd %H\" --date=format:\'%Y %m %d\' | awk \'{ if (y!=$1) { y=$1; last=$0; print $0 } else  { print last }}\' | sort -nr | uniq -c | sed -e \'s/^ *\\([0-9]\\+\\) \\(.\\+\\)/\\2 \\1/\'").read().split("\n")
		for commitIndex in range(len(commits)):
			commit = commits[commitIndex]
			if (commit == ""):
				continue

			print commit + " - " + str(commitIndex) + "/" + str(len(commits)) + " - ",
			commitSplit = commit.split(" ")

			# time execution
			start_time = timeit.default_timer()

			# set output file name
			filename = commitSplit[0] + "_" + commitSplit[1] + "_" + commitSplit[2] + "_" + commitSplit[3] + ".csv"
			# check if revision has been analysed
			if (os.path.isfile(output_dir + filename)):
				print "skipped"
				continue
			# checkout commit
			os.popen("git checkout -f " + commitSplit[3] + " 2>/dev/null")
			# fiter files using git ls-files
			os.popen("git ls-files > files")
			os.popen("cloc --list-file=files --by-file --csv --out=" + output_dir + filename)

			# parse cloc output
			f = open(output_dir + filename)
			reader = csv.reader(f)

			ids = []
			loc = []
			i = 0
			for item in reader:
				if (item[0] != 'language'):
					ids.append(item[1])
					loc.append(int(item[2])+int(item[3])+int(item[4]))
			f.close()

			# write to output file
			f = open(output_dir + filename, "w")
			f.write("id,weight\n")

			for j in range(0, len(ids)):
				f.write("%s,%d\n" % (ids[j], loc[j]))

			f.close()
			i += 1
			print str(timeit.default_timer() - start_time)[:6], "s"
