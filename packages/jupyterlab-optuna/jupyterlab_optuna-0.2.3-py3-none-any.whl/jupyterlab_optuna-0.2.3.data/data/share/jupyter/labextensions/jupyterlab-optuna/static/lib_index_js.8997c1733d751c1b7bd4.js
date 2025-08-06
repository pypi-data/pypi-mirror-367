"use strict";
(self["webpackChunkjupyterlab_optuna"] = self["webpackChunkjupyterlab_optuna"] || []).push([["lib_index_js"],{

/***/ "./img/optuna_logo.svg":
/*!*****************************!*\
  !*** ./img/optuna_logo.svg ***!
  \*****************************/
/***/ ((module) => {

module.exports = "<svg class=\"optuna-animation\" xmlns=\"http://www.w3.org/2000/svg\" width=\"294.7\" height=\"280\" viewBox=\"0 0 221 210\">\n    <path fill=\"rgb(6, 71, 135)\" d=\"M104.5.6c-31.2 4.6-55 16.5-74.5 37A107.3 107.3 0 0 0 3.2 84.9a78.4 78.4 0 0 0-2.6 24.6c0 12.5.3 16.4 2.2 23.5a114.2 114.2 0 0 0 19.5 38 114 114 0 0 0 103.3 37.5 111.6 111.6 0 0 0 83.1-63.1 100.3 100.3 0 0 0 11-44.9c.4-11.5.1-15.7-1.5-23.5a85.3 85.3 0 0 0-25.1-47.1 98 98 0 0 0-49.4-27c-8-2-31.9-3.4-39.2-2.3zm35.3 16.8A90 90 0 0 1 206.7 80a112 112 0 0 1 0 40.8 103.3 103.3 0 0 1-73.7 72 76.6 76.6 0 0 1-25 2.5 77 77 0 0 1-23.2-2.1 99.6 99.6 0 0 1-68.4-66.7 64 64 0 0 1-2.8-22.5c-.1-11.3.3-14.8 2.2-21.4C25.5 49.2 53.6 25 92.5 16.9a156 156 0 0 1 47.3.5z\"/>\n    <path fill=\"rgb(12, 97, 152)\" d=\"M94.6 29.5A88.3 88.3 0 0 0 68 39.1c-17 8.8-30.5 22-38.1 37.4a56.4 56.4 0 0 0-6.7 32c.9 18.9 7.2 32.1 22.7 47.5 13 12.8 25.8 20 44.9 25.2 11 3 31.5 2.9 42.7-.1a85.5 85.5 0 0 0 61.1-60.1c2.3-8.8 2.4-26.3.1-35a78.6 78.6 0 0 0-55.2-54.6 74.9 74.9 0 0 0-23.5-3c-9.9-.2-16.7.1-21.4 1.1zm37.2 11.1a61 61 0 0 1 29.7 17.9 55 55 0 0 1 18.6 43.6c.3 39.1-30.4 68.9-71.1 69.1-16.9 0-30-4.1-42.5-13.4A59.7 59.7 0 0 1 47.1 83c15.6-33 51.5-51 84.7-42.4z\"/>\n    <path fill=\"rgb(39, 126, 170)\" d=\"M96 57.6a58.6 58.6 0 0 0-40 35 43 43 0 0 0 1.6 30.4 62.8 62.8 0 0 0 20.2 22.6 70.7 70.7 0 0 0 28.8 10c34.6 3.2 64.7-28.1 58-60.4a50 50 0 0 0-37.3-37.7c-7.2-1.9-24-1.8-31.3.1zm31.9 16.1A32 32 0 0 1 148 93.4c.7 2.4 1.1 6.8.8 11.5a28 28 0 0 1-3.8 13.9 43.4 43.4 0 0 1-18.8 17.9c-5.2 2.5-6.7 2.8-16.7 2.8-9.8 0-11.6-.3-16.7-2.7-17.2-8-24.7-25.5-17.6-41a43.9 43.9 0 0 1 52.7-22.1z\"/>\n    <path fill=\"rgb(77, 154, 184)\" d=\"M109.5 86.9c-12.1 3-20.9 13.7-19.1 23.4 2.6 14.1 25 17.3 37.4 5.4 4.5-4.3 6.4-8.1 6.4-13.1.2-11.4-11.6-18.8-24.7-15.7zm7.7 11.8c4.5 4 .5 13.3-5.7 13.3-4.3 0-6.5-2.2-6.5-6.6 0-6.6 7.6-10.9 12.2-6.7z\"/>\n</svg>\n";

/***/ }),

/***/ "./lib/apiClient.js":
/*!**************************!*\
  !*** ./lib/apiClient.js ***!
  \**************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   JupyterlabAPIClient: () => (/* binding */ JupyterlabAPIClient)
/* harmony export */ });
/* harmony import */ var _optuna_optuna_dashboard__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @optuna/optuna-dashboard */ "webpack/sharing/consume/default/@optuna/optuna-dashboard/@optuna/optuna-dashboard");
/* harmony import */ var _optuna_optuna_dashboard__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_optuna_optuna_dashboard__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _handler__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./handler */ "./lib/handler.js");


class JupyterlabAPIClient extends _optuna_optuna_dashboard__WEBPACK_IMPORTED_MODULE_0__.APIClient {
    // biome-ignore lint/complexity/noUselessConstructor: <explanation>
    constructor() {
        super();
        this.getMetaInfo = () => (0,_handler__WEBPACK_IMPORTED_MODULE_1__.requestAPI)("/api/meta").then((res) => res);
        this.getStudyDetail = (studyId, nLocalTrials) => (0,_handler__WEBPACK_IMPORTED_MODULE_1__.requestAPI)(`/api/studies/${studyId}/?after=${nLocalTrials}`, {
            method: "GET",
        }).then((res) => {
            var _a, _b;
            const trials = res.trials.map((trial) => {
                return this.convertTrialResponse(trial);
            });
            const best_trials = res.best_trials.map((trial) => {
                return this.convertTrialResponse(trial);
            });
            return {
                id: studyId,
                name: res.name,
                datetime_start: new Date(res.datetime_start),
                directions: res.directions,
                user_attrs: res.user_attrs,
                trials: trials,
                best_trials: best_trials,
                union_search_space: res.union_search_space,
                intersection_search_space: res.intersection_search_space,
                union_user_attrs: res.union_user_attrs,
                has_intermediate_values: res.has_intermediate_values,
                note: res.note,
                objective_names: res.objective_names,
                form_widgets: res.form_widgets,
                is_preferential: res.is_preferential,
                feedback_component_type: res.feedback_component_type,
                preferences: res.preferences,
                preference_history: (_a = res.preference_history) === null || _a === void 0 ? void 0 : _a.map(this.convertPreferenceHistory),
                plotly_graph_objects: res.plotly_graph_objects,
                artifacts: res.artifacts,
                skipped_trial_numbers: (_b = res.skipped_trial_numbers) !== null && _b !== void 0 ? _b : [],
            };
        });
        this.getStudySummaries = () => (0,_handler__WEBPACK_IMPORTED_MODULE_1__.requestAPI)("/api/studies").then((res) => {
            return res.study_summaries.map((study) => {
                return {
                    study_id: study.study_id,
                    study_name: study.study_name,
                    directions: study.directions,
                    user_attrs: study.user_attrs,
                    is_preferential: study.is_preferential,
                    datetime_start: study.datetime_start
                        ? new Date(study.datetime_start)
                        : undefined,
                };
            });
        });
        this.createNewStudy = (studyName, directions) => (0,_handler__WEBPACK_IMPORTED_MODULE_1__.requestAPI)("/api/studies", {
            body: JSON.stringify({
                study_name: studyName,
                directions,
            }),
            method: "POST",
        }).then((res) => {
            const study_summary = res.study_summary;
            return {
                study_id: study_summary.study_id,
                study_name: study_summary.study_name,
                directions: study_summary.directions,
                // best_trial: undefined,
                user_attrs: study_summary.user_attrs,
                is_preferential: study_summary.is_preferential,
                datetime_start: study_summary.datetime_start
                    ? new Date(study_summary.datetime_start)
                    : undefined,
            };
        });
        this.deleteStudy = (studyId, removeAssociatedArtifacts) => (0,_handler__WEBPACK_IMPORTED_MODULE_1__.requestAPI)(`/api/studies/${studyId}`, {
            method: "DELETE",
            body: JSON.stringify({
                remove_associated_artifacts: removeAssociatedArtifacts,
            }),
        }).then(() => {
            return;
        });
        this.renameStudy = (studyId, studyName) => (0,_handler__WEBPACK_IMPORTED_MODULE_1__.requestAPI)(`/api/studies/${studyId}/rename`, {
            body: JSON.stringify({ study_name: studyName }),
            method: "POST",
        }).then((res) => {
            return {
                study_id: res.study_id,
                study_name: res.study_name,
                directions: res.directions,
                user_attrs: res.user_attrs,
                is_preferential: res.is_prefential,
                datetime_start: res.datetime_start
                    ? new Date(res.datetime_start)
                    : undefined,
            };
        });
        this.saveStudyNote = (studyId, note) => (0,_handler__WEBPACK_IMPORTED_MODULE_1__.requestAPI)(`/api/studies/${studyId}/note`, {
            body: JSON.stringify(note),
            method: "PUT",
        }).then(() => {
            return;
        });
        this.saveTrialNote = (studyId, trialId, note) => (0,_handler__WEBPACK_IMPORTED_MODULE_1__.requestAPI)(`/api/studies/${studyId}/${trialId}/note`, {
            body: JSON.stringify(note),
            method: "PUT",
        }).then(() => {
            return;
        });
        this.uploadTrialArtifact = (studyId, trialId, fileName, dataUrl) => (0,_handler__WEBPACK_IMPORTED_MODULE_1__.requestAPI)(`/api/artifacts/${studyId}/${trialId}`, {
            body: JSON.stringify({
                file: dataUrl,
                filename: fileName,
            }),
            method: "POST",
        }).then((res) => {
            return res;
        });
        this.uploadStudyArtifact = (studyId, fileName, dataUrl) => (0,_handler__WEBPACK_IMPORTED_MODULE_1__.requestAPI)(`/api/artifacts/${studyId}`, {
            body: JSON.stringify({
                file: dataUrl,
                filename: fileName,
            }),
            method: "POST",
        }).then((res) => {
            return res;
        });
        this.deleteTrialArtifact = (studyId, trialId, artifactId) => (0,_handler__WEBPACK_IMPORTED_MODULE_1__.requestAPI)(`/api/artifacts/${studyId}/${trialId}/${artifactId}`, {
            method: "DELETE",
        }).then(() => {
            return;
        });
        this.deleteStudyArtifact = (studyId, artifactId) => (0,_handler__WEBPACK_IMPORTED_MODULE_1__.requestAPI)(`/api/artifacts/${studyId}/${artifactId}`, {
            method: "DELETE",
        }).then(() => {
            return;
        });
        this.tellTrial = async (trialId, state, values) => {
            const req = {
                state: state,
                values: values,
            };
            await (0,_handler__WEBPACK_IMPORTED_MODULE_1__.requestAPI)(`/api/trials/${trialId}/tell`, {
                body: JSON.stringify(req),
                method: "POST",
            });
        };
        this.saveTrialUserAttrs = async (trialId, user_attrs) => {
            const req = { user_attrs: user_attrs };
            await (0,_handler__WEBPACK_IMPORTED_MODULE_1__.requestAPI)(`/api/trials/${trialId}/user-attrs`, {
                body: JSON.stringify(req),
                method: "POST",
            });
            return;
        };
        this.getParamImportances = (studyId) => (0,_handler__WEBPACK_IMPORTED_MODULE_1__.requestAPI)(`/api/studies/${studyId}/param_importances`).then((res) => {
            return res.param_importances;
        });
        this.reportPreference = (studyId, candidates, clicked) => (0,_handler__WEBPACK_IMPORTED_MODULE_1__.requestAPI)(`/api/studies/${studyId}/preference`, {
            body: JSON.stringify({
                candidates: candidates,
                clicked: clicked,
                mode: "ChooseWorst",
            }),
            method: "POST",
        }).then(() => {
            return;
        });
        this.skipPreferentialTrial = (studyId, trialId) => (0,_handler__WEBPACK_IMPORTED_MODULE_1__.requestAPI)(`/api/studies/${studyId}/${trialId}/skip`, {
            method: "POST",
        }).then(() => {
            return;
        });
        this.removePreferentialHistory = (studyId, historyUuid) => (0,_handler__WEBPACK_IMPORTED_MODULE_1__.requestAPI)(`/api/studies/${studyId}/preference/${historyUuid}`, {
            method: "DELETE",
        }).then(() => {
            return;
        });
        this.restorePreferentialHistory = (studyId, historyUuid) => (0,_handler__WEBPACK_IMPORTED_MODULE_1__.requestAPI)(`/api/studies/${studyId}/preference/${historyUuid}`, {
            method: "POST",
        }).then(() => {
            return;
        });
        this.reportFeedbackComponent = (studyId, component_type) => (0,_handler__WEBPACK_IMPORTED_MODULE_1__.requestAPI)(`/api/studies/${studyId}/preference_feedback_component`, {
            body: JSON.stringify({ component_type: component_type }),
            method: "POST",
        }).then(() => {
            return;
        });
        this.getPlot = (studyId, plotType) => (0,_handler__WEBPACK_IMPORTED_MODULE_1__.requestAPI)(`/api/studies/${studyId}/plot/${plotType}`).then((res) => res);
        this.getCompareStudiesPlot = (studyIds, plotType) => {
            return (0,_handler__WEBPACK_IMPORTED_MODULE_1__.requestAPI)(`/api/compare-studies/plot/${plotType}`, {
                body: JSON.stringify({ study_ids: studyIds }),
            }).then((res) => res);
        };
    }
    callTrialFilterQuery(request) {
        throw new Error("Trial filter query is not implemented in JupyterLab API client.");
    }
}


/***/ }),

/***/ "./lib/components/Debounce.js":
/*!************************************!*\
  !*** ./lib/components/Debounce.js ***!
  \************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   DebouncedInputTextField: () => (/* binding */ DebouncedInputTextField)
/* harmony export */ });
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @mui/material */ "./node_modules/@mui/material/TextField/TextField.js");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_1__);


const DebouncedInputTextField = ({ onChange, delay, textFieldProps }) => {
    const [text, setText] = react__WEBPACK_IMPORTED_MODULE_1___default().useState("");
    const [valid, setValidity] = react__WEBPACK_IMPORTED_MODULE_1___default().useState(true);
    // biome-ignore lint/correctness/useExhaustiveDependencies: <explanation>
    (0,react__WEBPACK_IMPORTED_MODULE_1__.useEffect)(() => {
        const timer = setTimeout(() => {
            onChange(text, valid);
        }, delay);
        return () => {
            clearTimeout(timer);
        };
    }, [text, delay]);
    return (react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__["default"], { onChange: (e) => {
            setText(e.target.value);
            setValidity(e.target.validity.valid);
        }, ...textFieldProps }));
};


/***/ }),

/***/ "./lib/components/JupyterLabEntrypoint.js":
/*!************************************************!*\
  !*** ./lib/components/JupyterLabEntrypoint.js ***!
  \************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   JupyterLabEntrypoint: () => (/* binding */ JupyterLabEntrypoint)
/* harmony export */ });
/* harmony import */ var _mui_icons_material_RestartAlt__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @mui/icons-material/RestartAlt */ "./node_modules/@mui/icons-material/esm/RestartAlt.js");
/* harmony import */ var _mui_icons_material_Start__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @mui/icons-material/Start */ "./node_modules/@mui/icons-material/esm/Start.js");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @mui/material */ "./node_modules/@mui/material/CssBaseline/CssBaseline.js");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @mui/material */ "./node_modules/@mui/material/Box/Box.js");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @mui/material */ "./node_modules/@mui/material/Typography/Typography.js");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @mui/material */ "./node_modules/@mui/material/Button/Button.js");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @mui/material */ "./node_modules/@mui/material/FormControl/FormControl.js");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! @mui/material */ "./node_modules/@mui/material/styles/createTheme.js");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! @mui/material */ "./node_modules/@mui/material/styles/useTheme.js");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! @mui/material */ "./node_modules/@mui/material/styles/ThemeProvider.js");
/* harmony import */ var _mui_material_CircularProgress__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__(/*! @mui/material/CircularProgress */ "./node_modules/@mui/material/CircularProgress/CircularProgress.js");
/* harmony import */ var _mui_material_colors__WEBPACK_IMPORTED_MODULE_11__ = __webpack_require__(/*! @mui/material/colors */ "./node_modules/@mui/material/colors/pink.js");
/* harmony import */ var _mui_material_colors__WEBPACK_IMPORTED_MODULE_12__ = __webpack_require__(/*! @mui/material/colors */ "./node_modules/@mui/material/colors/blue.js");
/* harmony import */ var _optuna_optuna_dashboard__WEBPACK_IMPORTED_MODULE_13__ = __webpack_require__(/*! @optuna/optuna-dashboard */ "webpack/sharing/consume/default/@optuna/optuna-dashboard/@optuna/optuna-dashboard");
/* harmony import */ var _optuna_optuna_dashboard__WEBPACK_IMPORTED_MODULE_13___default = /*#__PURE__*/__webpack_require__.n(_optuna_optuna_dashboard__WEBPACK_IMPORTED_MODULE_13__);
/* harmony import */ var notistack__WEBPACK_IMPORTED_MODULE_14__ = __webpack_require__(/*! notistack */ "./node_modules/notistack/notistack.esm.js");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_15__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_15___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_15__);
/* harmony import */ var _apiClient__WEBPACK_IMPORTED_MODULE_16__ = __webpack_require__(/*! ../apiClient */ "./lib/apiClient.js");
/* harmony import */ var _handler__WEBPACK_IMPORTED_MODULE_17__ = __webpack_require__(/*! ../handler */ "./lib/handler.js");
/* harmony import */ var _Debounce__WEBPACK_IMPORTED_MODULE_18__ = __webpack_require__(/*! ./Debounce */ "./lib/components/Debounce.js");











const jupyterlabAPIClient = new _apiClient__WEBPACK_IMPORTED_MODULE_16__.JupyterlabAPIClient();
const JupyterLabEntrypoint = () => {
    const [ready, setReady] = (0,react__WEBPACK_IMPORTED_MODULE_15__.useState)(false);
    const [pathName, setPathName] = (0,react__WEBPACK_IMPORTED_MODULE_15__.useState)("");
    // JupyterLab's theme switching is handled by setting CSS variables (ref: https://github.com/jupyterlab/jupyterlab/issues/4919#issuecomment-405757623).
    // Therefore, the implementation of determining whether JupyterLab is in dark or light mode should rely on these CSS variables.
    // The CSS variable used is defined here: https://github.com/jupyterlab/jupyterlab/blob/d470c501f50ad7075413cd89967a1a8a332b9a2f/packages/theme-light-extension/style/variables.css#L36
    const colorMode = getComputedStyle(document.querySelector(":root")).getPropertyValue("--jp-shadow-base-lightness") === "0"
        ? "light"
        : "dark";
    const theme = (0,react__WEBPACK_IMPORTED_MODULE_15__.useMemo)(() => (0,_mui_material__WEBPACK_IMPORTED_MODULE_7__["default"])({
        palette: {
            mode: colorMode,
            primary: _mui_material_colors__WEBPACK_IMPORTED_MODULE_12__["default"],
            secondary: _mui_material_colors__WEBPACK_IMPORTED_MODULE_11__["default"],
        },
    }), [colorMode]);
    (0,react__WEBPACK_IMPORTED_MODULE_15__.useEffect)(() => {
        setPathName(window.location.pathname);
    }, []);
    if (!ready) {
        return (react__WEBPACK_IMPORTED_MODULE_15___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_9__["default"], { theme: theme },
            react__WEBPACK_IMPORTED_MODULE_15___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_2__["default"], null),
            react__WEBPACK_IMPORTED_MODULE_15___default().createElement(notistack__WEBPACK_IMPORTED_MODULE_14__.SnackbarProvider, { maxSnack: 3 },
                react__WEBPACK_IMPORTED_MODULE_15___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_3__["default"], { sx: {
                        minHeight: "100vh",
                        display: "flex",
                        flexDirection: "column",
                        justifyContent: "center",
                        alignItems: "center",
                        backgroundColor: theme.palette.background.default,
                    } },
                    react__WEBPACK_IMPORTED_MODULE_15___default().createElement(JupyterLabStartWidget, { showOptunaDashboard: () => {
                            setReady(true);
                        } })))));
    }
    return (react__WEBPACK_IMPORTED_MODULE_15___default().createElement(_optuna_optuna_dashboard__WEBPACK_IMPORTED_MODULE_13__.ConstantsContext.Provider, { value: {
            color_mode: colorMode,
            environment: "jupyterlab",
            url_prefix: pathName,
        } },
        react__WEBPACK_IMPORTED_MODULE_15___default().createElement(_optuna_optuna_dashboard__WEBPACK_IMPORTED_MODULE_13__.APIClientProvider, { apiClient: jupyterlabAPIClient },
            react__WEBPACK_IMPORTED_MODULE_15___default().createElement(_optuna_optuna_dashboard__WEBPACK_IMPORTED_MODULE_13__.App, null))));
};
const JupyterLabStartWidget = ({ showOptunaDashboard }) => {
    const [loading, setLoading] = (0,react__WEBPACK_IMPORTED_MODULE_15__.useState)(true);
    const [isInitialized, setIsInitialized] = (0,react__WEBPACK_IMPORTED_MODULE_15__.useState)(false);
    const [cwd, setCwd] = (0,react__WEBPACK_IMPORTED_MODULE_15__.useState)("");
    (0,react__WEBPACK_IMPORTED_MODULE_15__.useEffect)(() => {
        setLoading(true);
        (0,_handler__WEBPACK_IMPORTED_MODULE_17__.requestAPI)("/api/is_initialized", {
            method: "GET",
        })
            .then((res) => {
            setIsInitialized(res.is_initialized);
            setCwd(res.cwd_path);
            setLoading(false);
        })
            .catch((err) => {
            setLoading(false);
            (0,notistack__WEBPACK_IMPORTED_MODULE_14__.enqueueSnackbar)("Failed to check the initialized state", {
                variant: "error",
            });
            console.error(err);
        });
    }, []);
    if (loading) {
        return (react__WEBPACK_IMPORTED_MODULE_15___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_3__["default"], { sx: {
                height: "100vh",
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
                alignItems: "center",
            } },
            react__WEBPACK_IMPORTED_MODULE_15___default().createElement(_mui_material_CircularProgress__WEBPACK_IMPORTED_MODULE_10__["default"], null)));
    }
    if (isInitialized) {
        return (react__WEBPACK_IMPORTED_MODULE_15___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_3__["default"], { sx: {
                display: "flex",
                flexDirection: "column",
                width: "600px",
                borderRadius: "8px",
                boxShadow: "rgba(0, 0, 0, 0.08) 0 8px 24px",
                padding: "64px",
            } },
            react__WEBPACK_IMPORTED_MODULE_15___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_4__["default"], { variant: "h4" }, "Continue or Reset?"),
            react__WEBPACK_IMPORTED_MODULE_15___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_4__["default"], { sx: { margin: "8px 0" } }, "Continue with the existing storage URL and artifact path settings, or you can reset them."),
            react__WEBPACK_IMPORTED_MODULE_15___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_5__["default"], { variant: "contained", onClick: showOptunaDashboard, color: "primary", startIcon: react__WEBPACK_IMPORTED_MODULE_15___default().createElement(_mui_icons_material_Start__WEBPACK_IMPORTED_MODULE_1__["default"], null), sx: { margin: "8px 0", minWidth: "120px" } }, "Continue"),
            react__WEBPACK_IMPORTED_MODULE_15___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_5__["default"], { variant: "outlined", onClick: () => {
                    setIsInitialized(false);
                }, color: "primary", startIcon: react__WEBPACK_IMPORTED_MODULE_15___default().createElement(_mui_icons_material_RestartAlt__WEBPACK_IMPORTED_MODULE_0__["default"], null), sx: { margin: "8px 0", minWidth: "120px" } }, "Reset")));
    }
    return (react__WEBPACK_IMPORTED_MODULE_15___default().createElement(StartDashboardForm, { showOptunaDashboard: showOptunaDashboard, cwd: cwd, setLoading: setLoading }));
};
const StartDashboardForm = ({ showOptunaDashboard, cwd, setLoading }) => {
    const theme = (0,_mui_material__WEBPACK_IMPORTED_MODULE_8__["default"])();
    const isDarkMode = theme.palette.mode === "dark";
    const [storageURL, setStorageURL] = (0,react__WEBPACK_IMPORTED_MODULE_15__.useState)("");
    const [artifactPath, setArtifactPath] = (0,react__WEBPACK_IMPORTED_MODULE_15__.useState)("");
    const [isValidURL, setIsValidURL] = (0,react__WEBPACK_IMPORTED_MODULE_15__.useState)(false);
    const handleValidateURL = (url) => {
        setIsValidURL(url !== "");
    };
    const handleCreateNewDashboard = () => {
        setLoading(true);
        (0,_handler__WEBPACK_IMPORTED_MODULE_17__.requestAPI)("/api/register_dashboard_app", {
            method: "POST",
            body: JSON.stringify({
                storage_url: storageURL,
                artifact_path: artifactPath,
            }),
        })
            .then((_res) => {
            setLoading(false);
            showOptunaDashboard();
        })
            .catch((err) => {
            setLoading(false);
            (0,notistack__WEBPACK_IMPORTED_MODULE_14__.enqueueSnackbar)("Failed to initialize Optuna Dashboard", {
                variant: "error",
            });
            console.error(err);
        });
    };
    return (react__WEBPACK_IMPORTED_MODULE_15___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_3__["default"], { sx: {
            display: "flex",
            flexDirection: "column",
            width: "600px",
            borderRadius: "8px",
            boxShadow: isDarkMode
                ? "rgba(255, 255, 255, 0.08) 0 8px 24px"
                : "rgba(0, 0, 0, 0.08) 0 8px 24px",
            padding: "64px",
        } },
        react__WEBPACK_IMPORTED_MODULE_15___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_4__["default"], { variant: "h4" }, "Initialize Dashboard"),
        react__WEBPACK_IMPORTED_MODULE_15___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_4__["default"], { sx: { margin: "8px 0" } },
            "Please enter a storage URL and an artifact path.",
            cwd !== "" && (react__WEBPACK_IMPORTED_MODULE_15___default().createElement((react__WEBPACK_IMPORTED_MODULE_15___default().Fragment), null,
                " ",
                "Your current working directory is ",
                react__WEBPACK_IMPORTED_MODULE_15___default().createElement("strong", null, cwd),
                "."))),
        react__WEBPACK_IMPORTED_MODULE_15___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_6__["default"], null,
            react__WEBPACK_IMPORTED_MODULE_15___default().createElement(_Debounce__WEBPACK_IMPORTED_MODULE_18__.DebouncedInputTextField, { onChange: (s) => {
                    handleValidateURL(s);
                    setStorageURL(s);
                }, delay: 500, textFieldProps: {
                    autoFocus: true,
                    fullWidth: true,
                    label: "Storage URL or File Path (Required)",
                    type: "text",
                    sx: { margin: "8px 0" },
                } })),
        react__WEBPACK_IMPORTED_MODULE_15___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_6__["default"], null,
            react__WEBPACK_IMPORTED_MODULE_15___default().createElement(_Debounce__WEBPACK_IMPORTED_MODULE_18__.DebouncedInputTextField, { onChange: (s) => {
                    setArtifactPath(s);
                }, delay: 500, textFieldProps: {
                    fullWidth: true,
                    label: "Artifact path (Optional)",
                    type: "text",
                    sx: { margin: "8px 0" },
                } })),
        react__WEBPACK_IMPORTED_MODULE_15___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_5__["default"], { variant: "contained", onClick: handleCreateNewDashboard, color: "primary", disabled: !isValidURL, sx: { margin: "8px 0" } }, "Create")));
};


/***/ }),

/***/ "./lib/handler.js":
/*!************************!*\
  !*** ./lib/handler.js ***!
  \************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   requestAPI: () => (/* binding */ requestAPI)
/* harmony export */ });
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/services */ "webpack/sharing/consume/default/@jupyterlab/services");
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__);


/**
 * Call the API extension
 *
 * @param endPoint API REST end point for the extension
 * @param init Initial values for the request
 * @returns The response body interpreted as JSON
 */
async function requestAPI(endPoint = "", init = {}) {
    // Make request to Jupyter API
    const settings = _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeSettings();
    const requestUrl = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.URLExt.join(settings.baseUrl, "jupyterlab-optuna", // API Namespace
    endPoint);
    let response;
    try {
        response = await _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeRequest(requestUrl, init, settings);
    }
    catch (error) {
        // biome-ignore lint/suspicious/noExplicitAny: <explanation>
        throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.NetworkError(error);
    }
    // biome-ignore lint/suspicious/noExplicitAny: <explanation>
    let data = await response.text();
    if (data.length > 0) {
        try {
            data = JSON.parse(data);
        }
        catch (error) {
            console.log("Not a JSON response body.", response);
        }
    }
    if (!response.ok) {
        throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.ResponseError(response, data.message || data);
    }
    return data;
}


/***/ }),

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _img_optuna_logo_svg__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../img/optuna_logo.svg */ "./img/optuna_logo.svg");
/* harmony import */ var _jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/launcher */ "webpack/sharing/consume/default/@jupyterlab/launcher");
/* harmony import */ var _jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _widget__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./widget */ "./lib/widget.js");






/**
 * The command IDs used by the server extension plugin.
 */
var CommandIDs;
(function (CommandIDs) {
    CommandIDs.get = "server:get-file";
    CommandIDs.ui = "server:dashboard-ui";
})(CommandIDs || (CommandIDs = {}));
/**
 * Initialization data for the jupyterlab-optuna extension.
 */
const plugin = {
    id: "jupyterlab-optuna:plugin",
    description: "A JupyterLab extension for Optuna",
    autoStart: true,
    optional: [_jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_2__.ILauncher],
    requires: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.ICommandPalette],
    activate: (app, palette, launcher) => {
        console.log("JupyterLab extension jupyterlab-optuna is activated!");
        console.log("ICommandPalette:", palette);
        const { commands, shell } = app;
        const optunaIcon = new _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_3__.LabIcon({
            name: "ui-components:optuna",
            svgstr: _img_optuna_logo_svg__WEBPACK_IMPORTED_MODULE_1__,
        });
        commands.addCommand(CommandIDs.ui, {
            caption: "Launch Optuna Dashboard",
            label: "Optuna Dashboard",
            icon: (args) => (args.isPalette ? undefined : optunaIcon),
            execute: () => {
                const content = new _widget__WEBPACK_IMPORTED_MODULE_4__.OptunaDashboardWidget();
                const widget = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.MainAreaWidget({ content });
                widget.title.label = "Optuna Dashboard Widget";
                widget.title.icon = optunaIcon;
                shell.add(widget, "main");
            },
        });
        if (launcher) {
            launcher.add({
                command: CommandIDs.ui,
            });
        }
        palette.addItem({ command: CommandIDs.ui, category: "Optuna" });
    },
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ }),

/***/ "./lib/widget.js":
/*!***********************!*\
  !*** ./lib/widget.js ***!
  \***********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   OptunaDashboardWidget: () => (/* binding */ OptunaDashboardWidget)
/* harmony export */ });
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _components_JupyterLabEntrypoint__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./components/JupyterLabEntrypoint */ "./lib/components/JupyterLabEntrypoint.js");



class OptunaDashboardWidget extends _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__.ReactWidget {
    constructor() {
        super();
        this.addClass("jp-react-widget");
    }
    render() {
        return react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_components_JupyterLabEntrypoint__WEBPACK_IMPORTED_MODULE_2__.JupyterLabEntrypoint, null);
    }
}


/***/ })

}]);
//# sourceMappingURL=lib_index_js.8997c1733d751c1b7bd4.js.map