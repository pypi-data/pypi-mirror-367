from __future__ import annotations

import re
from typing import Any

import numpy as np
import pandas as pd

from fiddler.packtools import gem
from fiddler.packtools.gem import GEMText

# pylint: disable=import-error,too-many-arguments,import-outside-toplevel


class IGTextAttributionsTF2Keras:
    """
    Helper class for project attribution method when computing IG for Text data with Keras TF2.
    """

    def __init__(self, input_df: pd.DataFrame, output_cols: list[str]) -> None:
        """
        :param input_df: pandas dataframe for a single observation
        :param output_cols: list of output column names
        """
        self.input_df = input_df
        self.output_cols = output_cols

    def text_to_tokens_keras(
        self, tokenizer: Any, max_seq_length: int, feature_label: str
    ) -> Any:
        """
        Helper function to convert text to tokens with keras TF2.

        :param tokenizer: keras tokenizer used during training
        :param max_seq_length: max sequence length used during training
        :param feature_label: str. Name of the text feature input
        :return: word tokens
        """
        from tensorflow.keras.preprocessing.sequence import pad_sequences

        unpadded_tokens = [
            tokenizer.texts_to_sequences([x])[0]
            for x in self.input_df[feature_label].values
        ]

        padded_tokens = pad_sequences(
            unpadded_tokens, max_seq_length, padding='post', truncating='post'
        )

        word_tokens = tokenizer.sequences_to_texts([[x] for x in padded_tokens[0]])
        return word_tokens

    def text_attributions(
        self,
        tokenizer: Any,
        word_tokens: Any,
        word_attributions: Any,
        feature_label: Any,
    ) -> tuple[list, list]:
        """
        Helper function to define segments works and attributions.

        :param tokenizer: keras tokenizer used during training
        :param word_tokens: word tokens. Could be the output of the text_to_tokens_keras method
        :param word_attributions: associated word attributions
        :param feature_label: str. Name of the text feature input
        :return: final segments and attributions
        """
        segments = re.split(
            r'([ ' + tokenizer.filters + '])',
            self.input_df.iloc[0][feature_label],
        )
        i = 0
        final_attributions = []
        final_segments = []
        for segment in segments:
            if segment != '':  # dump empty tokens
                final_segments.append(segment)
                seg_low = segment.lower()
                if len(word_tokens) > i and seg_low == word_tokens[i]:
                    final_attributions.append(word_attributions[i])
                    i += 1
                else:
                    final_attributions.append(0)
        return final_segments, final_attributions

    def get_attribution_for_output(
        self,
        att: dict[str, Any],
        word_tokens: Any,
        tokenizer: Any,
        embedding_name: str,
        feature_label: str,
    ) -> GEMText:
        """
        Helper function to get attributions for a given output.

        :param att: dictionary of attributions for the given output
        :param word_tokens: word tokens
        :param tokenizer: keras tokenizer used during training
        :param embedding_name: str. Name of the embedding layer in the model
        :param feature_label: str. Name of the text feature input
        :return:
        """
        # Note - summing over attributions in the embedding direction
        word_attributions = np.sum(att[embedding_name][-len(word_tokens) :], axis=1)
        final_segments, final_attributions = self.text_attributions(
            tokenizer, word_tokens, word_attributions, feature_label
        )
        gem_text = gem.GEMText(
            feature_name=feature_label,
            text_segments=final_segments,
            text_attributions=final_attributions,
        )

        return gem_text

    def get_project_attribution(
        self,
        attributions: Any,
        tokenizer: Any,
        word_tokens: Any,
        embedding_name: str,
        feature_label: str,
    ) -> dict[str, dict]:
        """
        Helper method to get project attributions when model has a single text input feature.

        :param attributions: list of IG attributions. Each element of the list corresponds to an output.
        :param tokenizer: tokenizer used during training
        :param word_tokens: word tokens
        :param embedding_name: str. Name of the embedding layer in the model
        :param feature_label: str. Name of the text feature input
        :return:
        """
        explanations_by_output = {}

        if isinstance(feature_label, list):
            if len(feature_label) == 1:
                feature_label = feature_label[0]
            else:
                raise ValueError(
                    'Your model has multiple inputs. You cannot use this helper. '
                    'Please implement project_attributions accordingly. '
                    'If you need some help, contact Fiddler.'
                )
        if isinstance(embedding_name, list):
            if len(embedding_name) == 1:
                embedding_name = embedding_name[0]
            else:
                raise ValueError(
                    'Your model has multiple embeddings. You cannot use this helper. '
                    'Please implement project_attributions accordingly. '
                    'If you need some help, contact Fiddler.'
                )

        for output_field_index, att in enumerate(attributions):
            gem_text = self.get_attribution_for_output(
                att, word_tokens, tokenizer, embedding_name, feature_label
            )
            gem_container = gem.GEMContainer(contents=[gem_text])
            explanations_by_output[self.output_cols[output_field_index]] = (
                gem_container.render()
            )

        return explanations_by_output


class IGTabularAttributions:
    """
    Helper class for project attribution method when computing IG for Tabular data.
    """

    def __init__(self, input_df: pd.DataFrame, output_cols: list[str]) -> None:
        """
        :param input_df: pandas dataframe for a single observation
        :param output_cols: list of output column names
        """
        self.input_df = input_df
        self.output_cols = output_cols

    def get_project_attribution(
        self, attributions: list[Any], attr_input_names_mapping: dict[str, Any]
    ) -> dict[str, dict]:
        """
        Helper method to get project attributions when input data is tabular.

        :param attributions: list of IG attributions. Each element of the list corresponds to an output.
        :param attr_input_names_mapping: dict that map attributable layer names to input feature names
        :return: dictionary explanations_by_output
        """
        explanations_by_output = {}
        if attr_input_names_mapping is None:
            raise ValueError(
                'Parameter attr_input_names_mapping cannot be empty when IG is enabled.'
            )
        for output_field_index, att in enumerate(attributions):
            explanations_by_output[self.output_cols[output_field_index]] = (
                get_tabular_attributions_for_output(
                    self.input_df,
                    att,
                    attr_input_names_mapping=attr_input_names_mapping,
                )
            )
        return explanations_by_output


class TreeShapAttributions:
    """
    Helper class for computing attributions with Tree SHAP for tree based model
    """

    def __init__(
        self,
        input_df: pd.DataFrame,
        transformed_df: pd.DataFrame,
        output_cols: list[str],
        model: Any,
    ) -> None:
        """
        :param input_df: pandas dataframe for a single observation
        :param transformed_df: pandas dataframe for a single transformed observation
               (if any pre-processing steps are required before running the model on the data)
        :param output_cols: list of output column names
        """
        import shap

        self.explainer = shap.TreeExplainer(model)
        self.input_df = input_df
        self.transformed_df = transformed_df
        self.output_cols = output_cols

    def get_project_attribution(
        self,
        predictions_dict: dict[str, Any],
        transformed_names_mapping: dict[str, Any] | None = None,
    ) -> tuple[dict[str, dict], dict[str, dict[str, float]]]:
        """
        Helper method to get project attributions for Tree SHAP.

        :param predictions_dict: dictionary of predictions of the model for the given input
        :param transformed_names_mapping: dictionary mapping feature name to corresponding transformed columns
        :return: dictionaries explanations_by_output, extras_by_output
        """
        if not isinstance(predictions_dict, dict):
            raise ValueError(
                'The parameter predictions_dict has to be a mapping dictionary between output col name '
                'and prediction value for the given input.'
            )
        if set(predictions_dict.keys()) != set(self.output_cols):
            raise ValueError(
                'The parameter predictions_dict has to have output col names as keys.'
            )

        shap_values = self.explainer.shap_values(
            self.transformed_df, check_additivity=False
        )
        untransformed_base_values = self.explainer.expected_value
        if isinstance(untransformed_base_values, float):
            untransformed_base_values = [untransformed_base_values]

        explanations_by_output = {}
        extras_by_output = {}

        if (transformed_names_mapping is None) and (
            set(self.input_df.columns) != set(self.transformed_df.columns)
        ):
            raise ValueError(
                'Your data has some pre-processing steps before being fed to the model. '
                'Please provide a dictionary with key feature names and values list of corresponding '
                'transformed feature names.'
            )

        for ind, output_name in enumerate(self.output_cols):
            if len(self.output_cols) == 1:
                if len(shap_values) == 2:
                    # For binary classification models that predict proba for 0 and 1
                    attributions = shap_values[1][0]
                else:
                    attributions = shap_values[0]
            else:
                attributions = shap_values[ind][0]

            # Transform shap values from log-odds to probability space
            shap_values_transformed, base_value = xgb_shap_transform_scale(
                attributions,
                model_prediction=predictions_dict[output_name],
                untransformed_base_value=untransformed_base_values[ind],
            )

            if transformed_names_mapping is not None:
                # Map the transformed input names to shap values
                map_att_transformed = {
                    name: shap_values_transformed[ind]
                    for ind, name in enumerate(self.transformed_df.columns)
                }
                # Map the original input names to sum of shap values
                shap_values_transformed = {
                    name: np.sum(
                        [
                            map_att_transformed[col]
                            for col in transformed_names_mapping[name]
                        ]
                    )
                    for name in transformed_names_mapping.keys()
                }
            explanations_by_output[output_name] = get_tabular_attributions_for_output(
                self.input_df, shap_values_transformed
            )

            extras_by_output[output_name] = {
                'model_prediction': predictions_dict[output_name],
                'baseline_prediction': base_value,
            }

        return explanations_by_output, extras_by_output


def get_tabular_attributions_for_output(  # noqa: C901
    input_df: pd.DataFrame,
    attributions: dict[str, Any],
    attr_input_names_mapping: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Helper function to get attributions for a single output.

    :param input_df: pandas dataframe for a single observation
    :param attributions: dictionary of attributions with keys attributable input names if IG is enabled.
                         Otherwise, this is just a list of attributions.
    :param attr_input_names_mapping: Required only if IG is enabled.
    :return: explanations for a single output
    """
    dense_features: list[gem.GEMBase] = []

    if attr_input_names_mapping is None:
        if isinstance(attributions, (list, np.ndarray)):
            attributions = {'dense_inputs': attributions}
            attr_input_names_mapping = {'dense_inputs': list(input_df.columns)}
        elif isinstance(attributions, dict):
            attr_input_names_mapping = {'dense_inputs': list(attributions.keys())}
            attributions = {'dense_inputs': list(attributions.values())}
        else:
            raise ValueError(
                f'The argument attributions should be a list or a dictionary mapping.'
                f" It's currently of type: {type(attributions)}"
            )

    for key in attributions.keys():
        if key not in attr_input_names_mapping:
            raise ValueError(
                f'The key {key} is missing in the attr_input_names_mapping dictionary.'
            )
        for ind, feature_name in enumerate(attr_input_names_mapping[key]):
            attr_val = attributions[key][ind]
            if isinstance(attr_val, (list, np.ndarray)):
                attr_val = np.sum(attr_val)
            value = input_df[feature_name].iloc[0]
            if pd.isnull(value):
                value = None
            dense_features.append(
                gem.GEMSimple(
                    feature_name=feature_name,
                    value=value,
                    attribution=float(attr_val),
                )
            )
        # Attribute 0.0 for features not used in the model
        missing_features = set(input_df.columns) - set(attr_input_names_mapping[key])
        for feature_name in missing_features:
            value = input_df[feature_name].iloc[0]
            if pd.isnull(value):
                value = None
            dense_features.append(
                gem.GEMSimple(
                    feature_name=feature_name,
                    value=value,
                    attribution=float(0.0),
                )
            )
    gem_container = gem.GEMContainer(contents=dense_features)

    return gem_container.render()


def xgb_shap_transform_scale(
    shap_values: Any, model_prediction: Any, untransformed_base_value: Any
) -> Any:
    base_value = 1 / (1 + np.exp(-untransformed_base_value))

    # Computing the original_explanation_distance to construct the distance_coefficient later on
    original_explanation_distance = np.sum(shap_values)  # type: ignore

    # Computing the distance between the model_prediction and the transformed base_value
    distance_to_explain = model_prediction - base_value

    if np.abs(distance_to_explain) <= 0.0001:
        # In that case, attributions are null
        shap_values_transformed = np.array([0.0] * len(shap_values))
    else:
        # The distance_coefficient is the ratio between both distances which will be used later on
        distance_coefficient = original_explanation_distance / distance_to_explain
        # Transforming the original shapley values to the new scale
        shap_values_transformed = shap_values / distance_coefficient

    return shap_values_transformed, base_value
