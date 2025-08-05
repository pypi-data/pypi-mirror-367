import hydra

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@hydra.main(version_base=None, config_path="../configs", config_name="eval.yaml")
def main(config):
    if config.model_type == 'silentcipher':
        from raw_bench.solver.silentcipher import SilentCipherSequential
        solver = SilentCipherSequential(config)

    elif config.model_type == 'audioseal':
        from raw_bench.solver.audioseal import SolverAudioSeal        
        solver = SolverAudioSeal(config)

    elif config.model_type == 'timbre':
        from raw_bench.solver.timbre import SolverTimbre
        solver = SolverTimbre(config)

    elif config.model_type == 'wavmark':
        from raw_bench.solver.wavmark import SolverWavMark
        solver = SolverWavMark(config)

    else:
        raise ValueError(f"Entered model type {config.model_type} not supported!")
        
    if config.mode == 'train':
        solver.train()

    elif config.mode == 'test':
        if config.checkpoint.load_dir is None:
             raise ValueError("load_ckpt must be provided in test mode")
        solver.eval(mode='test', write_to_disk=True)

    else:
         raise ValueError(f"Entered mode {config.mode} not supported!")
    
 
if __name__ == '__main__':
    main()