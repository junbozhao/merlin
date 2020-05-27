import argparse
import os
import socket
import shutil
import subprocess


parser = argparse.ArgumentParser(description="Launch 35 merlin workflow jobs")
parser.add_argument("run_id", type=int, help="The ID of this run")
parser.add_argument("output_path", type=str, help="the output path")
parser.add_argument("spec_path", type=str, help="path to the spec to run")
parser.add_argument("script_path", type=str, help="path to the make samples script")
args = parser.parse_args()
 
machine = socket.gethostbyaddr(socket.gethostname())[0]
if "quartz" in machine:
    machine == "quartz"
elif "pascal" in machine:
    machine == "pascal"

# launch 35 merlin workflow jobs
submit_path = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
concurrencies = [1, 2, 4, 8, 16, 32, 64]
nodes = [1, 1, 1, 1, 1, 1, 2]
samples = [1, 10, 100, 1000, 10000]
output_path = os.path.join(args.output_path, f"run_{args.run_id}")
os.makedirs(output_path, exist_ok=True)
for i, concurrency in enumerate(concurrencies):
    c_name = os.path.join(output_path, f"c_{concurrency}")
    if not os.path.isdir(c_name):
        os.mkdir(c_name)
    os.chdir(c_name)
    for j, sample in enumerate(samples):
        s_name = os.path.join(c_name, f"s_{sample}")
        if not os.path.isdir(s_name):
            os.mkdir(s_name)
        os.chdir(s_name)
        os.mkdir("scripts")
        samp_per_worker = float(sample) / float(concurrency)
        #if (samp_per_worker / 60) > times[j]:
        #    print(f"c{concurrency}_s{sample} : {round(samp_per_worker / 60, 0)}m.\ttime: {times[j]}m.\tdiff: {round((samp_per_worker / 60) - times[j], 0)}m")
        if (samp_per_worker / 60) < 1.0:
            real_time = 4
        elif (samp_per_worker / 60) < 3.0:
            real_time = 10
        else:
            real_time = samp_per_worker / 60
            real_time *= 2
            real_time = int(round(real_time, 0))
        # print(f"c{concurrency}_s{sample} : {real_time}")
        if machine == "quartz":
            account = "lbpm"
            partition = "pdebug"
        elif machine == "pascal":
            account = "wbronze"
            partition = "pvis"
        if real_time > 60:
            partition = "pbatch"
        submit = "submit.sbatch"
        command = f"sbatch -J c{concurrency}s{sample}r{args.run_id} --time {real_time} -N {nodes[i]} -p {partition} -A {account} {submit} {sample} {int(concurrency/nodes[i])} {args.run_id} {concurrency}"
        shutil.copyfile(os.path.join(submit_path, submit), submit)
        shutil.copyfile(args.spec_path, "spec.yaml")
        shutil.copyfile(args.script_path, os.path.join("scripts", "make_samples.py"))
        lines = subprocess.check_output(command, shell=True).decode("ascii")
        os.chdir(f"..")
    os.chdir(f"..")
