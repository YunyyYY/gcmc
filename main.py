from comet_ml import Experiment
import torch
import yaml

from src.dataset import MCDataset
from src.model import GAE
from src.train import Trainer
from src.utils import calc_rmse, random_init, init_xavier, Config


def main(config, comet=False):
    config = Config(config)

    # comet-ml setting
    if comet:
        experiment = Experiment(api_key=config.api_key,
                        project_name=config.project_name, workspace=config.workspace)
        experiment.log_parameters(config)

    # device and dataset setting
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    dataset = MCDataset(config.root, config.dataset_name)
    data = dataset[0].to(device)

    config.num_nodes = dataset.num_nodes
    config.num_users = int(data.num_users)
    config.num_relations = dataset.num_relations  # defines number of edge types

    # set and init model
    model = GAE(config, random_init).to(device)
    model.apply(init_xavier)

    # train
    if comet:
        trainer = Trainer(model, dataset, data, calc_rmse, config.epochs,
                config.lr, config.weight_decay, experiment)
    else:
        trainer = Trainer(model, dataset, data, calc_rmse,
                config.epochs, config.lr, config.weight_decay)
    trainer.iterate()


if __name__ == '__main__':
    with open('config.yml') as f:
        config = yaml.safe_load(f)
    main(config)
