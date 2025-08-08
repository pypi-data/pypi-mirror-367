
command="srun --partition=tamirQ --nodes=1 --ntasks=1 --gres=gpu:0 --cpus-per-task=1 --time=1:00:00 --mem=2G"
srun --partition=gpu-general --nodes=1  -A gpu-general-users --ntasks=1 --gres=gpu:1 --cpus-per-task=1 --time=1:00:00 --mem=50G --pty bash

sbatch --partition=gpu-general -t 7200 --nodes=1 -A gpu-general-users --ntasks=1 --gres=gpu:1 --cpus-per-task=1 submit_job_slurm_persist

sbatch -t 7200 job_notebook_slurm.sh

ssh -N -L 25243:compute-0-53:25243 nicolaslynn@power9login.tau.ac.il
ssh -N -L 4675:compute-0-340:4675 nicolaslynn@power9login.tau.ac.il
ssh -N -L 4674:compute-0-53:4674 nicolaslynn@powerslurm-login.tau.ac.il
ssh -N -L 4673:compute-0-340:4673 nicolaslynn@power9login.tau.ac.il

sbatch --gres=gpu:1 -p gpu-general -A gpu-general-users submit_job_slurm