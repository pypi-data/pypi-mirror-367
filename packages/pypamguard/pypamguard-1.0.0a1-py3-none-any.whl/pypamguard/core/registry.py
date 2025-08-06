# registry.py
# A module for registering the available modules (subclasses of PAMChunk)

from pypamguard.chunks.generics import GenericModule
from pypamguard.core.exceptions import ModuleNotFoundException

from pypamguard.chunks.modules.processing.ais import AISProcessing
ais_config = AISProcessing

from pypamguard.chunks.modules.detectors.click import ClickDetector
from pypamguard.chunks.modules.detectors.clicktriggerbackground import ClickTriggerBackground
click_config = {
    "Clicks": ClickDetector,
    "Trigger Background": ClickTriggerBackground,
}

from pypamguard.chunks.modules.processing.clipgenerator import ClipGenerator
clipgenerator_config = ClipGenerator

from pypamguard.chunks.modules.classifiers.deeplearningclassifier import DLCDetections, DLCModels
deeplearningclassifier_config = {
    "DL_detection": DLCDetections,
    "DL detection": DLCDetections,
    "DL_Model_Data": DLCModels,
    "DL Model Data": DLCModels,
}

from pypamguard.chunks.modules.processing.dbht import DbHtProcessing
dbht_config = DbHtProcessing

from pypamguard.chunks.modules.processing.difar import DIFARProcessing
difar_config = DIFARProcessing

from pypamguard.chunks.modules.processing.noisemonitor import NoiseMonitor
noisemonitor_config = NoiseMonitor

from pypamguard.chunks.modules.processing.noiseband import NoiseBandMonitor
noiseband_config = NoiseBandMonitor

from pypamguard.chunks.modules.detectors.gpl import GPLDetector
gpl_config = GPLDetector

from pypamguard.chunks.modules.detectors.rwedge import RWEdgeDetector
rwedge_config = RWEdgeDetector

from pypamguard.chunks.modules.detectors.whistleandmoan import WhistleAndMoanDetector
whistleandmoan_config = WhistleAndMoanDetector

from pypamguard.chunks.modules.processing.longtermspectralaverage import LongTermSpectralAverage
longtermspectralaverage_config = LongTermSpectralAverage

from pypamguard.chunks.modules.processing.ishmael import IshmaelData, IshmaelDetections
ishmael_config = {
    "Ishmael Peak Data": IshmaelData, # Not currently output from the detector
    "Ishmael Detections": IshmaelDetections,
}

from pypamguard.chunks.modules.plugins.spermwhaleipi import SpermWhaleIPI
spermwhaleipi_config = SpermWhaleIPI

from pypamguard.chunks.modules.plugins.geminithreshold import GeminiThresholdDetector
geminithreshold_config = GeminiThresholdDetector

MODULES = {
    "AIS Processing": ais_config,
    "Click Detector": click_config,
    "SoundTrap Click Detector": click_config,
    "Clip Generator": clipgenerator_config,
    "Deep Learning Classifier": deeplearningclassifier_config,
    "DbHt": dbht_config,
    "DIFAR Processing": difar_config,
    "LTSA": longtermspectralaverage_config,
    "Noise Monitor": noisemonitor_config,
    "Noise Band": noisemonitor_config,
    "NoiseBand": noiseband_config,
    "GPL Detector": gpl_config,
    "RW Edge Detector": rwedge_config,
    "WhistlesMoans": whistleandmoan_config,
    "Energy Sum Detector": ishmael_config,
    "Spectrogram Correlation Detector": ishmael_config,
    "Matched Filter Detector": ishmael_config,
    "Ipi module": spermwhaleipi_config,
    "Gemini Threshold Detector": geminithreshold_config,
}

def module_metadata(module):
    return {
        "name": module,
        "class": MODULES[module],
        "minimum_version": MODULES[module]._minimum_version,
        "maximum_version": MODULES[module]._maximum_version,
    }


class ModuleRegistry:
    def __init__(self):
        self.modules = {}
        register_preinstalled_modules(self)

    def register_module(self, module_name: str, module_class: GenericModule | dict):
        """Register a new module (must be a subclass of GenericModule or a dictionary)"""
        if module_name in self.modules:
            raise ValueError(f"Module {module_name} is already registered. Deregister module first by calling `deregister_module('{module_name}')`.")
        self.modules[module_name] = module_class
    
    def deregister_module(self, module_name: str) -> int:
        """Deregister a module. Returns the number of modules deregistered (either 0 or 1)"""
        if module_name in self.modules:
            del self.modules[module_name]
            return 1
        return 0
    
    def get_module(self, module_name: str, module_stream) -> GenericModule:
        if module_name in self.modules and type(self.modules[module_name]) == dict:
            if module_stream in self.modules[module_name]: return self.modules[module_name][module_stream]
            raise ModuleNotFoundException(f"Module '{module_name}' is not registered for stream '{module_stream}'.")
        elif module_name in self.modules and issubclass(self.modules[module_name], GenericModule):
            return self.modules[module_name]
        elif module_name in self.modules:
            raise ModuleNotFoundException(f"Module '{module_name}' is not registered correctly.")
        else:
            raise ModuleNotFoundException(f"Module '{module_name}' is not registered.")

def register_preinstalled_modules(registry: ModuleRegistry):

    for module in MODULES:
        registry.register_module(module, MODULES[module])
