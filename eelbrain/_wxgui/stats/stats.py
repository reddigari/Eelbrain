import wx

from ..frame import EelbrainFrame
from .roi import RegionOfInterest
from .info import InfoPanel
from .params import TestParams, SpatiotemporalSettings
from .model import TestModelInfo
from .stats_results import StatsResultsFrame
from .utils import ValidationException
from ... import testnd, set_parc


class StatsFrame(EelbrainFrame):

    add_params = dict(proportion=0, flag=wx.EXPAND | wx.ALL, border=10)

    def __init__(self, parent, loader=None, ds=None):
        super().__init__(parent, id=wx.ID_ANY)
        self.loader = loader
        self.ds = ds
        self.roi_info = None
        self.InitWidgets()
        self.InitUI()
        self.Show()
        self.Raise()

    def InitWidgets(self):
        self.info_panel = InfoPanel(self, self.loader, self.ds)
        self.spatiotemp = SpatiotemporalSettings(self)
        self.test_model = TestModelInfo(self, self.loader)
        self.test_params = TestParams(self)
        self.roi_dialog = wx.Button(self, label="Select ROI")
        self.roi_status = wx.StaticText(self, label="No ROI Selected")
        self.submit = wx.Button(self, label="Run Test")
        self.Bind(wx.EVT_BUTTON, self.run_test, self.submit)
        self.Bind(wx.EVT_RADIOBOX, self.test_params.toggle_minsource,
                  self.spatiotemp.choice)
        self.Bind(wx.EVT_BUTTON, self.OnROIMenuClick, self.roi_dialog)

    def InitUI(self):
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        for widget in (self.info_panel, self.spatiotemp, self.test_model,
                       self.test_params, self.roi_dialog, self.roi_status,
                       self.submit):
            self.sizer.Add(widget, **self.add_params)
        self.SetSizer(self.sizer)
        self.sizer.Layout()
        self.sizer.Fit(self)

    def get_test_kwargs(self):
        kwargs = dict()
        kwargs.update(self.test_model.get_test_kwargs())
        kwargs.update(self.test_params.get_test_kwargs())
        return kwargs

    def get_data_for_test(self):
        info = self.roi_info
        if info is None:
            raise RuntimeError("No ROI information provided.")
        subjects = self.info_panel.subj_sel.get_selected_subjects()
        idx = self.ds["subject"].isin(subjects)
        ds = self.ds.sub(idx)
        test_type = self.test_model.get_test_type()
        if test_type == "t-test":
            model = self.test_model.get_test_kwargs()
            sub_exp = "{}.isin(('{}', '{}'))".format(
                model["x"], model["c0"], model["c1"]
            )
            ds = ds.sub(sub_exp)
        src = ds["src"]
        src = set_parc(src, info["atlas"])
        if self.spatiotemp.is_temporal():
            data = src.summary(source=info["labels"])
        else:
            data = src.sub(source=info["labels"])
        return ds, data

    def run_test(self, evt):
        if not self.validate_all():
            return
        # TODO: handle correction over multiple regions
        test_type = self.test_model.get_test_type()
        if test_type == "ANOVA":
            test_func = testnd.anova
        elif test_type == "t-test":
            test_func = testnd.ttest_rel
        ds, data = self.get_data_for_test()
        kwargs = self.get_test_kwargs()
        if self.spatiotemp.is_temporal():
            del kwargs["minsource"]
        try:
            res = test_func(data, ds=ds, match="subject", **kwargs)
        except Exception as e:
            wx.MessageBox(str(e), "Test Failed")
        else:
            _ = StatsResultsFrame(None, res, ds, data)

    def OnROIMenuClick(self, evt):
        with RegionOfInterest(self, self.ds["src"], self.roi_info) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                self.roi_info = dlg.get_roi_info()
                self.roi_status.SetLabel(dlg.get_roi_status_string())
                self.sizer.Layout()
                self.sizer.Fit(self)
            else:
                pass
            dlg.Destroy()

    def validate_all(self):
        widgets = (self.info_panel, self.test_model, self.test_params)
        errors = []
        for widget in widgets:
            try:
                if isinstance(widget, TestParams):
                    widget.validate(self.ds["src"].time)
                else:
                    widget.validate()
            except ValidationException as e:
                errors.append(str(e))
        if self.roi_info is None or not self.roi_info["labels"]:
            errors.append("No brain regions selected.")
        if errors:
            message = "\n\n".join(errors)
            wx.MessageBox(message, "Invalid Test Parameters", wx.OK)
            return False
        return True