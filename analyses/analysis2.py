from common.analysisbase import AnalysisBase


class Analysis(AnalysisBase):
    def filename(self):
        return f"test/analysis2_M{self.parameters['mass']}GeV.json"

    def signalname(self):
        return f"signal_M{self.parameters['mass']}GeV"
