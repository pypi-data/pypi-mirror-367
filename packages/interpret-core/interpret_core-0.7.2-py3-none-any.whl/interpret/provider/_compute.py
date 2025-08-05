# Copyright (c) 2023 The InterpretML Contributors
# Distributed under the MIT software license

from abc import ABC, abstractmethod

from joblib import Parallel, delayed


class ComputeProvider(ABC):
    @abstractmethod
    def parallel(self, compute_fn, compute_args_iter):
        pass  # pragma: no cover


class JobLibProvider(ComputeProvider):
    def __init__(self, n_jobs=-1):
        self.n_jobs = n_jobs

    def parallel(self, compute_fn, compute_args_iter):
        return Parallel(n_jobs=self.n_jobs)(
            delayed(compute_fn)(*args) for args in compute_args_iter
        )


# NOTE: Not implemented yet
class AzureMLProvider(ComputeProvider):
    def parallel(self, compute_fn, compute_args_iter):
        raise NotImplementedError
