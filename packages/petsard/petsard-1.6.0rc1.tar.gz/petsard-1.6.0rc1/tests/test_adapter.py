from unittest.mock import Mock, patch

import pandas as pd
import pytest

from petsard.adapter import (
    BaseAdapter,
    ConstrainerAdapter,
    EvaluatorAdapter,
    LoaderAdapter,
    PreprocessorAdapter,
    ReporterAdapter,
    SplitterAdapter,
    SynthesizerAdapter,
)
from petsard.exceptions import ConfigError
from petsard.metadater import SchemaMetadata


class TestBaseAdapter:
    """測試 BaseAdapter 基礎類別"""

    def test_init_with_valid_config(self):
        """測試使用有效配置初始化"""
        config = {"method": "test", "param": "value"}

        class TestOperator(BaseAdapter):
            def _run(self, input):
                pass

            def set_input(self, status):
                return {}

            def get_result(self):
                return None

            def get_metadata(self):
                return Mock(spec=SchemaMetadata)

        operator = TestOperator(config)

        assert operator.config == config
        assert operator.module_name == "TestOp"
        assert operator.input == {}

    def test_init_with_none_config(self):
        """測試使用 None 配置初始化"""

        class TestOperator(BaseAdapter):
            def _run(self, input):
                pass

            def set_input(self, status):
                return {}

            def get_result(self):
                return None

            def get_metadata(self):
                return Mock(spec=SchemaMetadata)

        with pytest.raises(ConfigError):
            TestOperator(None)

    def test_run_template_method(self):
        """測試 run 模板方法"""
        config = {"method": "test"}

        class TestOperator(BaseAdapter):
            def __init__(self, config):
                super().__init__(config)
                self.run_called = False

            def _run(self, input):
                self.run_called = True

            def set_input(self, status):
                return {}

            def get_result(self):
                return None

            def get_metadata(self):
                return Mock(spec=SchemaMetadata)

        operator = TestOperator(config)

        with patch("time.time", side_effect=[1000.0, 1001.0, 1001.0]):
            with patch.object(operator, "_logger") as mock_logger:
                operator.run({})

        assert operator.run_called

        # 驗證計時 logging 訊息
        mock_logger.info.assert_any_call("TIMING_START|TestOp|run|1000.0")
        mock_logger.info.assert_any_call("Starting TestOp execution")
        mock_logger.info.assert_any_call("TIMING_END|TestOp|run|1001.0|1.0")

    def test_log_and_raise_config_error_decorator(self):
        """測試配置錯誤裝飾器"""
        config = {"method": "test"}

        class TestOperator(BaseAdapter):
            def _run(self, input):
                pass

            def get_result(self):
                return None

            def get_metadata(self):
                return Mock(spec=SchemaMetadata)

            @BaseAdapter.log_and_raise_config_error
            def set_input(self, status):
                raise ValueError("Test error")

        operator = TestOperator(config)

        with pytest.raises(ConfigError):
            operator.set_input(Mock())

    def test_not_implemented_methods(self):
        """測試未實作方法的錯誤"""
        config = {"method": "test"}
        operator = BaseAdapter(config)

        with pytest.raises(NotImplementedError):
            operator._run({})

        with pytest.raises(NotImplementedError):
            operator.set_input(Mock())

        with pytest.raises(NotImplementedError):
            operator.get_result()

        with pytest.raises(NotImplementedError):
            operator.get_metadata()

    def test_run_with_error_timing(self):
        """測試錯誤情況下的計時記錄"""
        config = {"method": "test"}

        class ErrorOperator(BaseAdapter):
            def _run(self, input):
                raise ValueError("Test error")

            def set_input(self, status):
                return {}

            def get_result(self):
                return None

            def get_metadata(self):
                return Mock(spec=SchemaMetadata)

        operator = ErrorOperator(config)

        with patch("time.time", side_effect=[1000.0, 1001.5, 1001.5]):
            with patch.object(operator, "_logger") as mock_logger:
                with pytest.raises(ValueError, match="Test error"):
                    operator.run({})

        # 驗證錯誤計時 logging 訊息
        mock_logger.info.assert_any_call("TIMING_START|ErrorOp|run|1000.0")
        mock_logger.info.assert_any_call("Starting ErrorOp execution")
        mock_logger.error.assert_any_call(
            "TIMING_ERROR|ErrorOp|run|1001.5|1.5|Test error"
        )


class TestLoaderAdapter:
    """測試 LoaderAdapter"""

    def test_init(self):
        """測試初始化"""
        config = {"method": "csv", "path": "test.csv"}

        with patch("petsard.adapter.Loader") as mock_loader_class:
            operator = LoaderAdapter(config)

            mock_loader_class.assert_called_once_with(**config)
            assert operator._schema_metadata is None

    def test_run(self):
        """測試執行"""
        config = {"method": "csv", "path": "test.csv"}
        test_data = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        mock_metadata = Mock(spec=SchemaMetadata)

        with patch("petsard.adapter.Loader") as mock_loader_class:
            mock_loader = Mock()
            mock_loader.load.return_value = (test_data, mock_metadata)
            mock_loader_class.return_value = mock_loader

            operator = LoaderAdapter(config)
            operator._run({})

            assert operator.data.equals(test_data)
            assert operator.metadata == mock_metadata
            assert operator._schema_metadata == mock_metadata

    def test_set_input(self):
        """測試輸入設定"""
        config = {"method": "csv", "path": "test.csv"}

        with patch("petsard.adapter.Loader"):
            operator = LoaderAdapter(config)
            mock_status = Mock()

            result = operator.set_input(mock_status)
            assert result == operator.input

    def test_get_result(self):
        """測試結果取得"""
        config = {"method": "csv", "path": "test.csv"}
        test_data = pd.DataFrame({"A": [1, 2, 3]})

        with patch("petsard.adapter.Loader"):
            operator = LoaderAdapter(config)
            operator.data = test_data

            result = operator.get_result()
            assert result.equals(test_data)

    def test_get_metadata(self):
        """測試元資料取得"""
        config = {"method": "csv", "path": "test.csv"}
        mock_metadata = Mock(spec=SchemaMetadata)

        with patch("petsard.adapter.Loader"):
            operator = LoaderAdapter(config)
            operator.metadata = mock_metadata

            result = operator.get_metadata()
            assert result == mock_metadata


class TestSplitterAdapter:
    """測試 SplitterAdapter"""

    def test_init(self):
        """測試初始化"""
        config = {"method": "random", "test_size": 0.2}

        with patch("petsard.adapter.Splitter") as mock_splitter_class:
            SplitterAdapter(config)

            mock_splitter_class.assert_called_once_with(**config)

    def test_run(self):
        """測試執行"""
        config = {"method": "random", "test_size": 0.2}
        input_data = {
            "data": pd.DataFrame({"A": [1, 2, 3]}),
            "metadata": Mock(spec=SchemaMetadata),
            "exist_train_indices": [],
        }

        with patch("petsard.adapter.Splitter") as mock_splitter_class:
            mock_splitter = Mock()
            mock_data = {
                1: {
                    "train": pd.DataFrame({"A": [1, 2]}),
                    "validation": pd.DataFrame({"A": [3]}),
                }
            }
            mock_metadata = Mock(spec=SchemaMetadata)
            mock_train_indices = {1: [0, 1]}
            mock_splitter.split.return_value = (
                mock_data,
                mock_metadata,
                mock_train_indices,
            )
            mock_splitter_class.return_value = mock_splitter

            operator = SplitterAdapter(config)
            operator._run(input_data)

            # Check that split was called with correct parameters
            # 空的 exist_train_indices 不會被傳遞
            expected_params = {
                "data": input_data["data"],
            }
            mock_splitter.split.assert_called_once_with(**expected_params)

            # Check that results are stored correctly
            assert operator.data == mock_data
            assert operator.metadata == mock_metadata
            assert operator.train_indices == mock_train_indices

    def test_set_input_with_data(self):
        """測試有資料的輸入設定"""
        config = {"test_size": 0.2}  # 沒有 method 參數
        test_data = pd.DataFrame({"A": [1, 2, 3]})
        mock_metadata = Mock(spec=SchemaMetadata)

        with patch("petsard.adapter.Splitter"):
            operator = SplitterAdapter(config)

            mock_status = Mock()
            mock_status.get_result.return_value = test_data
            mock_status.get_metadata.return_value = mock_metadata
            mock_status.get_exist_train_indices.return_value = []

            result = operator.set_input(mock_status)

            assert result["data"].equals(test_data)
            assert result["metadata"] == mock_metadata
            assert result["exist_train_indices"] == []

    def test_set_input_custom_method(self):
        """測試自定義方法的輸入設定"""
        config = {"method": "custom_data"}

        with patch("petsard.adapter.Splitter"):
            operator = SplitterAdapter(config)

            mock_status = Mock()
            mock_status.get_exist_train_indices.return_value = []

            result = operator.set_input(mock_status)

            assert result["data"] is None
            assert result["exist_train_indices"] == []

    def test_get_result(self):
        """測試結果取得"""
        config = {"method": "random"}
        test_result = {
            "train": pd.DataFrame({"A": [1, 2]}),
            "validation": pd.DataFrame({"A": [3]}),
        }

        with patch("petsard.adapter.Splitter") as mock_splitter_class:
            mock_splitter_class.return_value = Mock()

            operator = SplitterAdapter(config)
            operator.data = {1: test_result}  # 直接設定在 operator 上
            result = operator.get_result()

            assert "train" in result
            assert "validation" in result

    def test_get_metadata(self):
        """測試元資料取得"""
        config = {"method": "random"}
        mock_metadata = Mock(spec=SchemaMetadata)

        with patch("petsard.adapter.Splitter") as mock_splitter_class:
            mock_splitter = Mock()
            mock_splitter_class.return_value = mock_splitter

            operator = SplitterAdapter(config)
            # 設定新的字典格式 metadata
            metadata_dict = {1: {"train": mock_metadata, "validation": mock_metadata}}
            operator.metadata = metadata_dict

            with patch(
                "petsard.adapter.deepcopy", return_value=mock_metadata
            ) as mock_deepcopy:
                result = operator.get_metadata()

                mock_deepcopy.assert_called_once_with(mock_metadata)
                assert result == mock_metadata

    def test_get_train_indices(self):
        """測試訓練索引取得"""
        config = {"method": "random"}
        mock_train_indices = {1: [0, 1, 2], 2: [3, 4, 5]}

        with patch("petsard.adapter.Splitter") as mock_splitter_class:
            mock_splitter = Mock()
            mock_splitter_class.return_value = mock_splitter

            operator = SplitterAdapter(config)
            operator.train_indices = mock_train_indices

            with patch(
                "petsard.adapter.deepcopy", return_value=mock_train_indices
            ) as mock_deepcopy:
                result = operator.get_train_indices()

                mock_deepcopy.assert_called_once_with(mock_train_indices)
                assert result == mock_train_indices


class TestPreprocessorAdapter:
    """測試 PreprocessorAdapter"""

    def test_init_default_method(self):
        """測試預設方法初始化"""
        config = {"method": "default"}

        operator = PreprocessorAdapter(config)

        assert operator.processor is None
        assert operator._config == {}
        assert operator._sequence is None

    def test_init_custom_method(self):
        """測試自定義方法初始化"""
        config = {
            "method": "custom",
            "param1": "value1",
            "sequence": ["encoder", "scaler"],
        }

        operator = PreprocessorAdapter(config)

        assert operator._sequence == ["encoder", "scaler"]
        assert "sequence" not in operator._config
        assert operator._config["param1"] == "value1"

    def test_run_default_sequence(self):
        """測試預設序列執行"""
        config = {"method": "default"}
        input_data = {
            "data": pd.DataFrame({"A": [1, 2, 3]}),
            "metadata": Mock(spec=SchemaMetadata),
        }

        with patch("petsard.adapter.Processor") as mock_processor_class:
            mock_processor = Mock()
            mock_processor.transform.return_value = pd.DataFrame({"A": [1, 2, 3]})
            mock_processor_class.return_value = mock_processor

            operator = PreprocessorAdapter(config)
            operator._run(input_data)

            mock_processor.fit.assert_called_once_with(data=input_data["data"])
            mock_processor.transform.assert_called_once_with(data=input_data["data"])

    def test_run_custom_sequence(self):
        """測試自定義序列執行"""
        config = {"method": "custom", "sequence": ["encoder", "scaler"]}
        input_data = {
            "data": pd.DataFrame({"A": [1, 2, 3]}),
            "metadata": Mock(spec=SchemaMetadata),
        }

        with patch("petsard.adapter.Processor") as mock_processor_class:
            mock_processor = Mock()
            mock_processor.transform.return_value = pd.DataFrame({"A": [1, 2, 3]})
            mock_processor_class.return_value = mock_processor

            operator = PreprocessorAdapter(config)
            operator._run(input_data)

            mock_processor.fit.assert_called_once_with(
                data=input_data["data"], sequence=["encoder", "scaler"]
            )

    def test_set_input_from_splitter(self):
        """測試從 Splitter 設定輸入"""
        config = {"method": "default"}

        operator = PreprocessorAdapter(config)

        mock_status = Mock()
        mock_status.get_pre_module.return_value = "Splitter"
        mock_status.get_result.return_value = {
            "train": pd.DataFrame({"A": [1, 2]}),
            "validation": pd.DataFrame({"A": [3]}),
        }
        mock_status.get_metadata.return_value = Mock(spec=SchemaMetadata)

        result = operator.set_input(mock_status)

        assert result["data"].equals(pd.DataFrame({"A": [1, 2]}))

    def test_set_input_from_loader(self):
        """測試從 Loader 設定輸入"""
        config = {"method": "default"}
        test_data = pd.DataFrame({"A": [1, 2, 3]})

        operator = PreprocessorAdapter(config)

        mock_status = Mock()
        mock_status.get_pre_module.return_value = "Loader"
        mock_status.get_result.return_value = test_data
        mock_status.get_metadata.return_value = Mock(spec=SchemaMetadata)

        result = operator.set_input(mock_status)

        assert result["data"].equals(test_data)

    def test_get_result(self):
        """測試結果取得"""
        config = {"method": "default"}
        test_data = pd.DataFrame({"A": [1, 2, 3]})

        operator = PreprocessorAdapter(config)
        operator.data_preproc = test_data

        with patch("petsard.adapter.deepcopy", return_value=test_data) as mock_deepcopy:
            result = operator.get_result()

            mock_deepcopy.assert_called_once_with(test_data)
            assert result.equals(test_data)

    def test_get_metadata(self):
        """測試元資料取得"""
        config = {"method": "default"}
        mock_metadata = Mock(spec=SchemaMetadata)

        with patch("petsard.adapter.Processor") as mock_processor_class:
            mock_processor = Mock()
            mock_processor._metadata = mock_metadata
            mock_processor._sequence = []
            mock_processor_class.return_value = mock_processor

            operator = PreprocessorAdapter(config)
            operator.processor = mock_processor

            with patch(
                "petsard.adapter.deepcopy", return_value=mock_metadata
            ) as mock_deepcopy:
                result = operator.get_metadata()

                mock_deepcopy.assert_called_once_with(mock_metadata)
                assert result == mock_metadata


class TestSynthesizerAdapter:
    """測試 SynthesizerAdapter"""

    def test_init(self):
        """測試初始化"""
        config = {"method": "sdv", "model": "GaussianCopula"}

        with patch("petsard.adapter.Synthesizer") as mock_synthesizer_class:
            operator = SynthesizerAdapter(config)

            mock_synthesizer_class.assert_called_once_with(**config)
            assert operator.data_syn is None

    def test_run(self):
        """測試執行"""
        config = {"method": "sdv", "model": "GaussianCopula"}
        input_data = {
            "data": pd.DataFrame({"A": [1, 2, 3]}),
            "metadata": Mock(spec=SchemaMetadata),
        }
        synthetic_data = pd.DataFrame({"A": [4, 5, 6]})

        with patch("petsard.adapter.Synthesizer") as mock_synthesizer_class:
            mock_synthesizer = Mock()
            mock_synthesizer.fit_sample.return_value = synthetic_data
            mock_synthesizer_class.return_value = mock_synthesizer

            operator = SynthesizerAdapter(config)
            operator._run(input_data)

            mock_synthesizer.create.assert_called_once_with(
                metadata=input_data["metadata"]
            )
            mock_synthesizer.fit_sample.assert_called_once_with(data=input_data["data"])
            assert operator.data_syn.equals(synthetic_data)

    def test_set_input_with_metadata(self):
        """測試有元資料的輸入設定"""
        config = {"method": "sdv"}
        test_data = pd.DataFrame({"A": [1, 2, 3]})
        mock_metadata = Mock(spec=SchemaMetadata)

        operator = SynthesizerAdapter(config)

        mock_status = Mock()
        mock_status.metadata = {"Loader": mock_metadata}
        mock_status.get_pre_module.return_value = "Loader"
        mock_status.get_metadata.return_value = mock_metadata
        mock_status.get_result.return_value = test_data

        # Mock the fields attribute to make metadata valid
        mock_metadata.fields = {"field1": "type1", "field2": "type2"}

        result = operator.set_input(mock_status)

        assert result["data"].equals(test_data)
        assert result["metadata"] == mock_metadata

    def test_set_input_without_metadata(self):
        """測試無元資料的輸入設定"""
        config = {"method": "sdv"}
        test_data = pd.DataFrame({"A": [1, 2, 3]})

        operator = SynthesizerAdapter(config)

        mock_status = Mock()
        mock_status.get_pre_module.return_value = "Loader"
        mock_status.get_result.return_value = test_data

        # Mock get_metadata to raise an exception (simulating no metadata)
        mock_status.get_metadata.side_effect = Exception("No metadata available")

        result = operator.set_input(mock_status)

        assert result["data"].equals(test_data)
        assert result["metadata"] is None

    def test_get_result(self):
        """測試結果取得"""
        config = {"method": "sdv"}
        synthetic_data = pd.DataFrame({"A": [1, 2, 3]})

        operator = SynthesizerAdapter(config)
        operator.data_syn = synthetic_data

        with patch(
            "petsard.adapter.deepcopy", return_value=synthetic_data
        ) as mock_deepcopy:
            result = operator.get_result()

            mock_deepcopy.assert_called_once_with(synthetic_data)
            assert result.equals(synthetic_data)


class TestConstrainerAdapter:
    """測試 ConstrainerAdapter"""

    def test_init_basic(self):
        """測試基本初始化"""
        config = {"field_constraints": {"A": {"min": 0, "max": 10}}}

        with patch("petsard.adapter.Constrainer") as mock_constrainer_class:
            operator = ConstrainerAdapter(config)

            mock_constrainer_class.assert_called_once()
            assert operator.sample_dict == {}

    def test_init_with_sampling_params(self):
        """測試包含採樣參數的初始化"""
        config = {
            "field_constraints": {"A": {"min": 0, "max": 10}},
            "target_rows": 1000,
            "sampling_ratio": 1.5,
            "max_trials": 100,
            "verbose_step": 10,
        }

        with patch("petsard.adapter.Constrainer"):
            operator = ConstrainerAdapter(config)

            assert operator.sample_dict["target_rows"] == 1000
            assert operator.sample_dict["sampling_ratio"] == 1.5
            assert operator.sample_dict["max_trials"] == 100
            assert operator.sample_dict["verbose_step"] == 10

    def test_transform_field_combinations(self):
        """測試欄位組合轉換"""
        config = {
            "field_combinations": [
                [{"field": "A", "value": 1}, {"field": "B", "value": 2}],
                [{"field": "C", "value": 3}, {"field": "D", "value": 4}],
            ]
        }

        with patch("petsard.adapter.Constrainer"):
            operator = ConstrainerAdapter(config)

            # 檢查是否轉換為 tuple
            transformed_config = operator.config
            assert isinstance(transformed_config["field_combinations"][0], tuple)
            assert isinstance(transformed_config["field_combinations"][1], tuple)

    def test_run_simple_apply(self):
        """測試簡單約束應用"""
        config = {"field_constraints": {"A": {"min": 0, "max": 10}}}
        input_data = {"data": pd.DataFrame({"A": [1, 2, 3]})}
        constrained_data = pd.DataFrame({"A": [1, 2, 3]})

        with patch("petsard.adapter.Constrainer") as mock_constrainer_class:
            mock_constrainer = Mock()
            mock_constrainer.apply.return_value = constrained_data
            mock_constrainer_class.return_value = mock_constrainer

            operator = ConstrainerAdapter(config)
            operator._run(input_data)

            mock_constrainer.apply.assert_called_once_with(input_data["data"])
            assert operator.constrained_data.equals(constrained_data)

    def test_run_resample_until_satisfy(self):
        """測試重採樣直到滿足約束"""
        config = {"field_constraints": {"A": {"min": 0, "max": 10}}, "target_rows": 100}
        input_data = {
            "data": pd.DataFrame({"A": [1, 2, 3]}),
            "synthesizer": Mock(),
            "postprocessor": Mock(),
        }
        constrained_data = pd.DataFrame({"A": [1, 2, 3]})

        with patch("petsard.adapter.Constrainer") as mock_constrainer_class:
            mock_constrainer = Mock()
            mock_constrainer.resample_until_satisfy.return_value = constrained_data
            mock_constrainer_class.return_value = mock_constrainer

            operator = ConstrainerAdapter(config)
            operator._run(input_data)

            mock_constrainer.resample_until_satisfy.assert_called_once()
            assert operator.constrained_data.equals(constrained_data)


class TestEvaluatorAdapter:
    """測試 EvaluatorAdapter"""

    def test_init(self):
        """測試初始化"""
        config = {"method": "sdmetrics"}

        with patch("petsard.adapter.Evaluator") as mock_evaluator_class:
            operator = EvaluatorAdapter(config)

            mock_evaluator_class.assert_called_once_with(**config)
            assert operator.evaluations is None

    def test_run(self):
        """測試執行"""
        config = {"method": "sdmetrics"}
        input_data = {
            "data": {
                "ori": pd.DataFrame({"A": [1, 2, 3]}),
                "syn": pd.DataFrame({"A": [4, 5, 6]}),
                "control": pd.DataFrame({"A": [7, 8, 9]}),
            }
        }
        evaluation_results = {"test_metric": pd.DataFrame({"score": [0.8]})}

        with patch("petsard.adapter.Evaluator") as mock_evaluator_class:
            mock_evaluator = Mock()
            mock_evaluator.eval.return_value = evaluation_results
            mock_evaluator_class.return_value = mock_evaluator

            operator = EvaluatorAdapter(config)
            operator._run(input_data)

            mock_evaluator.create.assert_called_once()
            mock_evaluator.eval.assert_called_once_with(**input_data)
            assert operator.evaluations == evaluation_results

    def test_set_input_with_splitter(self):
        """測試有 Splitter 的輸入設定"""
        config = {"method": "sdmetrics"}

        operator = EvaluatorAdapter(config)

        mock_status = Mock()
        mock_status.status = {"Splitter": Mock()}
        mock_status.get_result.side_effect = lambda module: {
            "Splitter": {
                "train": pd.DataFrame({"A": [1, 2]}),
                "validation": pd.DataFrame({"A": [3]}),
            },
            "Synthesizer": pd.DataFrame({"A": [4, 5]}),
        }[module]
        mock_status.get_pre_module.return_value = "Synthesizer"

        result = operator.set_input(mock_status)

        assert "ori" in result["data"]
        assert "syn" in result["data"]
        assert "control" in result["data"]

    def test_set_input_without_splitter(self):
        """測試無 Splitter 的輸入設定"""
        config = {"method": "sdmetrics"}

        operator = EvaluatorAdapter(config)

        mock_status = Mock()
        mock_status.status = {}
        mock_status.get_result.side_effect = lambda module: {
            "Loader": pd.DataFrame({"A": [1, 2, 3]}),
            "Synthesizer": pd.DataFrame({"A": [4, 5, 6]}),
        }[module]
        mock_status.get_pre_module.return_value = "Synthesizer"

        result = operator.set_input(mock_status)

        assert "ori" in result["data"]
        assert "syn" in result["data"]
        assert "control" not in result["data"]


class TestReporterAdapter:
    """測試 ReporterAdapter"""

    def test_init(self):
        """測試初始化"""
        config = {"method": "save_report"}

        with patch("petsard.adapter.Reporter") as mock_reporter_class:
            operator = ReporterAdapter(config)

            mock_reporter_class.assert_called_once_with(**config)
            assert operator.report == {}

    def test_run_save_report(self):
        """測試儲存報告執行"""
        config = {"method": "save_report", "granularity": "global"}
        input_data = {"data": {"test_data": pd.DataFrame({"A": [1, 2, 3]})}}

        with patch("petsard.adapter.Reporter") as mock_reporter_class:
            mock_reporter = Mock()
            # 新的函式化設計：create() 返回結果而不是存儲在 result 中
            result_data = {
                "Reporter": {
                    "[global]": {
                        "eval_expt_name": "[global]",
                        "granularity": "global",
                        "report": pd.DataFrame({"metric": [0.8, 0.9]}),
                    }
                }
            }
            mock_reporter.create.return_value = result_data
            mock_reporter.report.return_value = result_data
            mock_reporter_class.return_value = mock_reporter

            operator = ReporterAdapter(config)
            operator._run(input_data)

            mock_reporter.create.assert_called_once_with(data=input_data["data"])
            mock_reporter.report.assert_called_once()
            assert "[global]" in operator.report

    def test_run_save_data(self):
        """測試儲存資料執行"""
        config = {"method": "save_data", "source": "test"}
        input_data = {"data": {"test_data": pd.DataFrame({"A": [1, 2, 3]})}}

        with patch("petsard.adapter.Reporter") as mock_reporter_class:
            mock_reporter = Mock()
            # 新的函式化設計：create() 返回結果
            result_data = {"saved_data": "path/to/saved/data"}
            mock_reporter.create.return_value = result_data
            mock_reporter.report.return_value = result_data
            mock_reporter_class.return_value = mock_reporter

            operator = ReporterAdapter(config)
            operator._run(input_data)

            assert operator.report == {"saved_data": "path/to/saved/data"}

    def test_set_input(self):
        """測試輸入設定"""
        config = {
            "method": "save_report",
            "source": ["Loader", "Synthesizer"],
            "granularity": "global",
        }

        operator = ReporterAdapter(config)

        mock_status = Mock()
        mock_status.get_full_expt.return_value = {
            "Loader": "load_data",
            "Synthesizer": "synthesize",
        }
        mock_status.get_result.side_effect = lambda module: {
            "Loader": pd.DataFrame({"A": [1, 2, 3]}),
            "Synthesizer": pd.DataFrame({"A": [4, 5, 6]}),
        }[module]
        mock_status.get_report.return_value = {}

        result = operator.set_input(mock_status)

        assert "data" in result
        assert "exist_report" in result["data"]

    def test_run_save_report_multi_granularity(self):
        """測試多 granularity 儲存報告執行"""
        config = {"method": "save_report", "granularity": ["global", "columnwise"]}
        input_data = {"data": {"test_data": pd.DataFrame({"A": [1, 2, 3]})}}

        with patch("petsard.adapter.Reporter") as mock_reporter_class:
            mock_reporter = Mock()
            # 多 granularity 結果格式
            result_data = {
                "Reporter": {
                    "test_[global]": {
                        "eval_expt_name": "test_[global]",
                        "granularity": "global",
                        "report": pd.DataFrame({"metric": [0.8]}),
                    },
                    "test_[columnwise]": {
                        "eval_expt_name": "test_[columnwise]",
                        "granularity": "columnwise",
                        "report": pd.DataFrame({"metric": [0.9, 0.7]}),
                    },
                }
            }
            mock_reporter.create.return_value = result_data
            mock_reporter.report.return_value = result_data
            mock_reporter_class.return_value = mock_reporter

            operator = ReporterAdapter(config)
            operator._run(input_data)

            mock_reporter.create.assert_called_once_with(data=input_data["data"])
            mock_reporter.report.assert_called_once()

            # 檢查多 granularity 結果
            assert "test_[global]" in operator.report
            assert "test_[columnwise]" in operator.report
            # 注意：report 中存儲的是 DataFrame，不包含 granularity 資訊
            assert isinstance(operator.report["test_[global]"], pd.DataFrame)
            assert isinstance(operator.report["test_[columnwise]"], pd.DataFrame)

    def test_run_save_report_new_granularity_types(self):
        """測試新的 granularity 類型（details, tree）"""
        config = {"method": "save_report", "granularity": ["details", "tree"]}
        input_data = {"data": {"test_data": pd.DataFrame({"A": [1, 2, 3]})}}

        with patch("petsard.adapter.Reporter") as mock_reporter_class:
            mock_reporter = Mock()
            # 新 granularity 類型結果格式
            result_data = {
                "Reporter": {
                    "test_[details]": {
                        "eval_expt_name": "test_[details]",
                        "granularity": "details",
                        "report": pd.DataFrame(
                            {"detail": ["detail1", "detail2"], "score": [0.8, 0.9]}
                        ),
                    },
                    "test_[tree]": {
                        "eval_expt_name": "test_[tree]",
                        "granularity": "tree",
                        "report": pd.DataFrame(
                            {"node": ["node1", "node2"], "score": [0.7, 0.6]}
                        ),
                    },
                }
            }
            mock_reporter.create.return_value = result_data
            mock_reporter.report.return_value = result_data
            mock_reporter_class.return_value = mock_reporter

            operator = ReporterAdapter(config)
            operator._run(input_data)

            # 檢查新 granularity 類型結果
            assert "test_[details]" in operator.report
            assert "test_[tree]" in operator.report
            # 注意：report 中存儲的是 DataFrame，不包含 granularity 資訊
            assert isinstance(operator.report["test_[details]"], pd.DataFrame)
            assert isinstance(operator.report["test_[tree]"], pd.DataFrame)

    def test_run_save_report_backward_compatibility(self):
        """測試向後相容性（舊格式結果）"""
        config = {"method": "save_report", "granularity": "global"}
        input_data = {"data": {"test_data": pd.DataFrame({"A": [1, 2, 3]})}}

        with patch("petsard.adapter.Reporter") as mock_reporter_class:
            mock_reporter = Mock()
            # 舊格式結果（向後相容）
            mock_reporter.create.return_value = {
                "Reporter": {
                    "eval_expt_name": "test_experiment",
                    "granularity": "global",
                    "report": pd.DataFrame({"metric": [0.8, 0.9]}),
                }
            }
            # Mock report() 方法返回 create() 的結果
            mock_reporter.report.return_value = mock_reporter.create.return_value
            mock_reporter_class.return_value = mock_reporter

            operator = ReporterAdapter(config)
            operator._run(input_data)

            # 檢查向後相容性
            assert "test_experiment" in operator.report
            assert isinstance(operator.report["test_experiment"], pd.DataFrame)

    def test_run_save_timing(self):
        """測試儲存時間執行"""
        config = {"method": "save_timing"}
        input_data = {"data": {"timing_data": pd.DataFrame({"duration": [1.0, 2.0]})}}

        with patch("petsard.adapter.Reporter") as mock_reporter_class:
            mock_reporter = Mock()
            timing_df = pd.DataFrame({"module": ["A", "B"], "duration": [1.0, 2.0]})
            mock_reporter.create.return_value = {"timing_report": timing_df}
            # Mock report() 方法返回 DataFrame（ReporterSaveTiming 的行為）
            mock_reporter.report.return_value = timing_df
            mock_reporter_class.return_value = mock_reporter

            operator = ReporterAdapter(config)
            operator._run(input_data)

            mock_reporter.create.assert_called_once_with(data=input_data["data"])
            mock_reporter.report.assert_called_once()
            assert "timing_report" in operator.report
            assert isinstance(operator.report["timing_report"], pd.DataFrame)


if __name__ == "__main__":
    pytest.main([__file__])
