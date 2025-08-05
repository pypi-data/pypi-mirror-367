# Copyright (C) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in project root for information.


import sys
if sys.version >= '3':
    basestring = str

from pyspark import SparkContext, SQLContext
from pyspark.sql import DataFrame
from pyspark.ml.param.shared import *
from pyspark import keyword_only
from pyspark.ml.util import JavaMLReadable, JavaMLWritable
from synapse.ml.core.platform import running_on_synapse_internal
from synapse.ml.core.serialize.java_params_patch import *
from pyspark.ml.wrapper import JavaTransformer, JavaEstimator, JavaModel
from pyspark.ml.evaluation import JavaEvaluator
from pyspark.ml.common import inherit_doc
from synapse.ml.core.schema.Utils import *
from pyspark.ml.param import TypeConverters
from synapse.ml.core.schema.TypeConversionUtils import generateTypeConverter, complexTypeConverter


@inherit_doc
class OpenAIPrompt(ComplexParamsMixin, JavaMLReadable, JavaMLWritable, JavaTransformer):
    """
    Args:
        AADToken (object): AAD Token used for authentication
        CustomAuthHeader (object): A Custom Value for Authorization Header
        apiVersion (object): version of the api
        bestOf (object): How many generations to create server side, and display only the best. Will not stream intermediate progress if best_of > 1. Has maximum value of 128.
        cacheLevel (object): can be used to disable any server-side caching, 0=no cache, 1=prompt prefix enabled, 2=full cache
        concurrency (int): max number of concurrent calls
        concurrentTimeout (float): max number seconds to wait on futures if concurrency >= 1
        customHeaders (object): Map of Custom Header Key-Value Tuples.
        customUrlRoot (str): The custom URL root for the service. This will not append OpenAI specific model path completions (i.e. /chat/completions) to the URL.
        deploymentName (object): The name of the deployment
        dropPrompt (bool): whether to drop the column of prompts after templating (when using legacy models)
        echo (object): Echo back the prompt in addition to the completion
        errorCol (str): column to hold http errors
        frequencyPenalty (object): How much to penalize new tokens based on whether they appear in the text so far. Increases the likelihood of the model to talk about new topics.
        logProbs (object): Include the log probabilities on the `logprobs` most likely tokens, as well the chosen tokens. So for example, if `logprobs` is 10, the API will return a list of the 10 most likely tokens. If `logprobs` is 0, only the chosen tokens will have logprobs returned. Minimum of 0 and maximum of 100 allowed.
        maxTokens (object): The maximum number of tokens to generate. Has minimum of 0.
        messagesCol (str): The column messages to generate chat completions for, in the chat format. This column should have type Array(Struct(role: String, content: String)).
        n (object): How many snippets to generate for each prompt. Minimum of 1 and maximum of 128 allowed.
        outputCol (str): The name of the output column
        postProcessing (str): Post processing options: csv, json, regex
        postProcessingOptions (dict): Options (default): delimiter=',', jsonSchema, regex, regexGroup=0
        presencePenalty (object): How much to penalize new tokens based on their existing frequency in the text so far. Decreases the likelihood of the model to repeat the same line verbatim. Has minimum of -2 and maximum of 2.
        promptTemplate (str): The prompt. supports string interpolation {col1}: {col2}.
        responseFormat (object): Response format for the completion. Can be 'json_object' or 'text'.
        stop (object): A sequence which indicates the end of the current document.
        subscriptionKey (object): the API key to use
        systemPrompt (str): The initial system prompt to be used.
        telemHeaders (object): Map of Custom Header Key-Value Tuples.
        temperature (object): What sampling temperature to use. Higher values means the model will take more risks. Try 0.9 for more creative applications, and 0 (argmax sampling) for ones with a well-defined answer. We generally recommend using this or `top_p` but not both. Minimum of 0 and maximum of 2 allowed.
        timeout (float): number of seconds to wait before closing the connection
        topP (object): An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10 percent probability mass are considered. We generally recommend using this or `temperature` but not both. Minimum of 0 and maximum of 1 allowed.
        url (str): Url of the service
        user (object): The ID of the end-user, for use in tracking and rate-limiting.
    """

    AADToken = Param(Params._dummy(), "AADToken", "ServiceParam: AAD Token used for authentication")
    
    CustomAuthHeader = Param(Params._dummy(), "CustomAuthHeader", "ServiceParam: A Custom Value for Authorization Header")
    
    apiVersion = Param(Params._dummy(), "apiVersion", "ServiceParam: version of the api")
    
    bestOf = Param(Params._dummy(), "bestOf", "ServiceParam: How many generations to create server side, and display only the best. Will not stream intermediate progress if best_of > 1. Has maximum value of 128.")
    
    cacheLevel = Param(Params._dummy(), "cacheLevel", "ServiceParam: can be used to disable any server-side caching, 0=no cache, 1=prompt prefix enabled, 2=full cache")
    
    concurrency = Param(Params._dummy(), "concurrency", "max number of concurrent calls", typeConverter=TypeConverters.toInt)
    
    concurrentTimeout = Param(Params._dummy(), "concurrentTimeout", "max number seconds to wait on futures if concurrency >= 1", typeConverter=TypeConverters.toFloat)
    
    customHeaders = Param(Params._dummy(), "customHeaders", "ServiceParam: Map of Custom Header Key-Value Tuples.")
    
    customUrlRoot = Param(Params._dummy(), "customUrlRoot", "The custom URL root for the service. This will not append OpenAI specific model path completions (i.e. /chat/completions) to the URL.", typeConverter=TypeConverters.toString)
    
    deploymentName = Param(Params._dummy(), "deploymentName", "ServiceParam: The name of the deployment")
    
    dropPrompt = Param(Params._dummy(), "dropPrompt", "whether to drop the column of prompts after templating (when using legacy models)", typeConverter=TypeConverters.toBoolean)
    
    echo = Param(Params._dummy(), "echo", "ServiceParam: Echo back the prompt in addition to the completion")
    
    errorCol = Param(Params._dummy(), "errorCol", "column to hold http errors", typeConverter=TypeConverters.toString)
    
    frequencyPenalty = Param(Params._dummy(), "frequencyPenalty", "ServiceParam: How much to penalize new tokens based on whether they appear in the text so far. Increases the likelihood of the model to talk about new topics.")
    
    logProbs = Param(Params._dummy(), "logProbs", "ServiceParam: Include the log probabilities on the `logprobs` most likely tokens, as well the chosen tokens. So for example, if `logprobs` is 10, the API will return a list of the 10 most likely tokens. If `logprobs` is 0, only the chosen tokens will have logprobs returned. Minimum of 0 and maximum of 100 allowed.")
    
    maxTokens = Param(Params._dummy(), "maxTokens", "ServiceParam: The maximum number of tokens to generate. Has minimum of 0.")
    
    messagesCol = Param(Params._dummy(), "messagesCol", "The column messages to generate chat completions for, in the chat format. This column should have type Array(Struct(role: String, content: String)).", typeConverter=TypeConverters.toString)
    
    n = Param(Params._dummy(), "n", "ServiceParam: How many snippets to generate for each prompt. Minimum of 1 and maximum of 128 allowed.")
    
    outputCol = Param(Params._dummy(), "outputCol", "The name of the output column", typeConverter=TypeConverters.toString)
    
    postProcessing = Param(Params._dummy(), "postProcessing", "Post processing options: csv, json, regex", typeConverter=TypeConverters.toString)
    
    postProcessingOptions = Param(Params._dummy(), "postProcessingOptions", "Options (default): delimiter=',', jsonSchema, regex, regexGroup=0")
    
    presencePenalty = Param(Params._dummy(), "presencePenalty", "ServiceParam: How much to penalize new tokens based on their existing frequency in the text so far. Decreases the likelihood of the model to repeat the same line verbatim. Has minimum of -2 and maximum of 2.")
    
    promptTemplate = Param(Params._dummy(), "promptTemplate", "The prompt. supports string interpolation {col1}: {col2}.", typeConverter=TypeConverters.toString)
    
    responseFormat = Param(Params._dummy(), "responseFormat", "ServiceParam: Response format for the completion. Can be 'json_object' or 'text'.")
    
    stop = Param(Params._dummy(), "stop", "ServiceParam: A sequence which indicates the end of the current document.")
    
    subscriptionKey = Param(Params._dummy(), "subscriptionKey", "ServiceParam: the API key to use")
    
    systemPrompt = Param(Params._dummy(), "systemPrompt", "The initial system prompt to be used.", typeConverter=TypeConverters.toString)
    
    telemHeaders = Param(Params._dummy(), "telemHeaders", "ServiceParam: Map of Custom Header Key-Value Tuples.")
    
    temperature = Param(Params._dummy(), "temperature", "ServiceParam: What sampling temperature to use. Higher values means the model will take more risks. Try 0.9 for more creative applications, and 0 (argmax sampling) for ones with a well-defined answer. We generally recommend using this or `top_p` but not both. Minimum of 0 and maximum of 2 allowed.")
    
    timeout = Param(Params._dummy(), "timeout", "number of seconds to wait before closing the connection", typeConverter=TypeConverters.toFloat)
    
    topP = Param(Params._dummy(), "topP", "ServiceParam: An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10 percent probability mass are considered. We generally recommend using this or `temperature` but not both. Minimum of 0 and maximum of 1 allowed.")
    
    url = Param(Params._dummy(), "url", "Url of the service", typeConverter=TypeConverters.toString)
    
    user = Param(Params._dummy(), "user", "ServiceParam: The ID of the end-user, for use in tracking and rate-limiting.")

    
    @keyword_only
    def __init__(
        self,
        java_obj=None,
        AADToken=None,
        AADTokenCol=None,
        CustomAuthHeader=None,
        CustomAuthHeaderCol=None,
        apiVersion=None,
        apiVersionCol=None,
        bestOf=None,
        bestOfCol=None,
        cacheLevel=None,
        cacheLevelCol=None,
        concurrency=1,
        concurrentTimeout=None,
        customHeaders=None,
        customHeadersCol=None,
        customUrlRoot=None,
        deploymentName=None,
        deploymentNameCol=None,
        dropPrompt=True,
        echo=None,
        echoCol=None,
        errorCol="OpenAIPrompt_cad80f291d0e_error",
        frequencyPenalty=None,
        frequencyPenaltyCol=None,
        logProbs=None,
        logProbsCol=None,
        maxTokens=None,
        maxTokensCol=None,
        messagesCol="OpenAIPrompt_cad80f291d0e_messages",
        n=None,
        nCol=None,
        outputCol="OpenAIPrompt_cad80f291d0e_output",
        postProcessing="",
        postProcessingOptions={},
        presencePenalty=None,
        presencePenaltyCol=None,
        promptTemplate=None,
        responseFormat=None,
        responseFormatCol=None,
        stop=None,
        stopCol=None,
        subscriptionKey=None,
        subscriptionKeyCol=None,
        systemPrompt="You are an AI chatbot who wants to answer user's questions and complete tasks. Follow their instructions carefully and be brief if they don't say otherwise.",
        telemHeaders=None,
        telemHeadersCol=None,
        temperature=None,
        temperatureCol=None,
        timeout=360.0,
        topP=None,
        topPCol=None,
        url=None,
        user=None,
        userCol=None
        ):
        super(OpenAIPrompt, self).__init__()
        if java_obj is None:
            self._java_obj = self._new_java_obj("com.microsoft.azure.synapse.ml.services.openai.OpenAIPrompt", self.uid)
        else:
            self._java_obj = java_obj
        self._setDefault(concurrency=1)
        self._setDefault(dropPrompt=True)
        self._setDefault(errorCol="OpenAIPrompt_cad80f291d0e_error")
        self._setDefault(messagesCol="OpenAIPrompt_cad80f291d0e_messages")
        self._setDefault(outputCol="OpenAIPrompt_cad80f291d0e_output")
        self._setDefault(postProcessing="")
        self._setDefault(postProcessingOptions={})
        self._setDefault(systemPrompt="You are an AI chatbot who wants to answer user's questions and complete tasks. Follow their instructions carefully and be brief if they don't say otherwise.")
        self._setDefault(timeout=360.0)
        if hasattr(self, "_input_kwargs"):
            kwargs = self._input_kwargs
        else:
            kwargs = self.__init__._input_kwargs
    
        if java_obj is None:
            for k,v in kwargs.items():
                if v is not None:
                    getattr(self, "set" + k[0].upper() + k[1:])(v)

    @keyword_only
    def setParams(
        self,
        AADToken=None,
        AADTokenCol=None,
        CustomAuthHeader=None,
        CustomAuthHeaderCol=None,
        apiVersion=None,
        apiVersionCol=None,
        bestOf=None,
        bestOfCol=None,
        cacheLevel=None,
        cacheLevelCol=None,
        concurrency=1,
        concurrentTimeout=None,
        customHeaders=None,
        customHeadersCol=None,
        customUrlRoot=None,
        deploymentName=None,
        deploymentNameCol=None,
        dropPrompt=True,
        echo=None,
        echoCol=None,
        errorCol="OpenAIPrompt_cad80f291d0e_error",
        frequencyPenalty=None,
        frequencyPenaltyCol=None,
        logProbs=None,
        logProbsCol=None,
        maxTokens=None,
        maxTokensCol=None,
        messagesCol="OpenAIPrompt_cad80f291d0e_messages",
        n=None,
        nCol=None,
        outputCol="OpenAIPrompt_cad80f291d0e_output",
        postProcessing="",
        postProcessingOptions={},
        presencePenalty=None,
        presencePenaltyCol=None,
        promptTemplate=None,
        responseFormat=None,
        responseFormatCol=None,
        stop=None,
        stopCol=None,
        subscriptionKey=None,
        subscriptionKeyCol=None,
        systemPrompt="You are an AI chatbot who wants to answer user's questions and complete tasks. Follow their instructions carefully and be brief if they don't say otherwise.",
        telemHeaders=None,
        telemHeadersCol=None,
        temperature=None,
        temperatureCol=None,
        timeout=360.0,
        topP=None,
        topPCol=None,
        url=None,
        user=None,
        userCol=None
        ):
        """
        Set the (keyword only) parameters
        """
        if hasattr(self, "_input_kwargs"):
            kwargs = self._input_kwargs
        else:
            kwargs = self.__init__._input_kwargs
        return self._set(**kwargs)

    @classmethod
    def read(cls):
        """ Returns an MLReader instance for this class. """
        return JavaMMLReader(cls)

    @staticmethod
    def getJavaPackage():
        """ Returns package name String. """
        return "com.microsoft.azure.synapse.ml.services.openai.OpenAIPrompt"

    @staticmethod
    def _from_java(java_stage):
        module_name=OpenAIPrompt.__module__
        module_name=module_name.rsplit(".", 1)[0] + ".OpenAIPrompt"
        return from_java(java_stage, module_name)

    def setAADToken(self, value):
        """
        Args:
            AADToken: AAD Token used for authentication
        """
        if isinstance(value, list):
            value = SparkContext._active_spark_context._jvm.com.microsoft.azure.synapse.ml.param.ServiceParam.toSeq(value)
        self._java_obj = self._java_obj.setAADToken(value)
        return self
    
    def setAADTokenCol(self, value):
        """
        Args:
            AADToken: AAD Token used for authentication
        """
        self._java_obj = self._java_obj.setAADTokenCol(value)
        return self
    
    def setCustomAuthHeader(self, value):
        """
        Args:
            CustomAuthHeader: A Custom Value for Authorization Header
        """
        if isinstance(value, list):
            value = SparkContext._active_spark_context._jvm.com.microsoft.azure.synapse.ml.param.ServiceParam.toSeq(value)
        self._java_obj = self._java_obj.setCustomAuthHeader(value)
        return self
    
    def setCustomAuthHeaderCol(self, value):
        """
        Args:
            CustomAuthHeader: A Custom Value for Authorization Header
        """
        self._java_obj = self._java_obj.setCustomAuthHeaderCol(value)
        return self
    
    def setApiVersion(self, value):
        """
        Args:
            apiVersion: version of the api
        """
        if isinstance(value, list):
            value = SparkContext._active_spark_context._jvm.com.microsoft.azure.synapse.ml.param.ServiceParam.toSeq(value)
        self._java_obj = self._java_obj.setApiVersion(value)
        return self
    
    def setApiVersionCol(self, value):
        """
        Args:
            apiVersion: version of the api
        """
        self._java_obj = self._java_obj.setApiVersionCol(value)
        return self
    
    def setBestOf(self, value):
        """
        Args:
            bestOf: How many generations to create server side, and display only the best. Will not stream intermediate progress if best_of > 1. Has maximum value of 128.
        """
        if isinstance(value, list):
            value = SparkContext._active_spark_context._jvm.com.microsoft.azure.synapse.ml.param.ServiceParam.toSeq(value)
        self._java_obj = self._java_obj.setBestOf(value)
        return self
    
    def setBestOfCol(self, value):
        """
        Args:
            bestOf: How many generations to create server side, and display only the best. Will not stream intermediate progress if best_of > 1. Has maximum value of 128.
        """
        self._java_obj = self._java_obj.setBestOfCol(value)
        return self
    
    def setCacheLevel(self, value):
        """
        Args:
            cacheLevel: can be used to disable any server-side caching, 0=no cache, 1=prompt prefix enabled, 2=full cache
        """
        if isinstance(value, list):
            value = SparkContext._active_spark_context._jvm.com.microsoft.azure.synapse.ml.param.ServiceParam.toSeq(value)
        self._java_obj = self._java_obj.setCacheLevel(value)
        return self
    
    def setCacheLevelCol(self, value):
        """
        Args:
            cacheLevel: can be used to disable any server-side caching, 0=no cache, 1=prompt prefix enabled, 2=full cache
        """
        self._java_obj = self._java_obj.setCacheLevelCol(value)
        return self
    
    def setConcurrency(self, value):
        """
        Args:
            concurrency: max number of concurrent calls
        """
        self._set(concurrency=value)
        return self
    
    def setConcurrentTimeout(self, value):
        """
        Args:
            concurrentTimeout: max number seconds to wait on futures if concurrency >= 1
        """
        self._set(concurrentTimeout=value)
        return self
    
    def setCustomHeaders(self, value):
        """
        Args:
            customHeaders: Map of Custom Header Key-Value Tuples.
        """
        if isinstance(value, list):
            value = SparkContext._active_spark_context._jvm.com.microsoft.azure.synapse.ml.param.ServiceParam.toSeq(value)
        self._java_obj = self._java_obj.setCustomHeaders(value)
        return self
    
    def setCustomHeadersCol(self, value):
        """
        Args:
            customHeaders: Map of Custom Header Key-Value Tuples.
        """
        self._java_obj = self._java_obj.setCustomHeadersCol(value)
        return self
    
    def setCustomUrlRoot(self, value):
        """
        Args:
            customUrlRoot: The custom URL root for the service. This will not append OpenAI specific model path completions (i.e. /chat/completions) to the URL.
        """
        self._set(customUrlRoot=value)
        return self
    
    def setDeploymentName(self, value):
        """
        Args:
            deploymentName: The name of the deployment
        """
        if isinstance(value, list):
            value = SparkContext._active_spark_context._jvm.com.microsoft.azure.synapse.ml.param.ServiceParam.toSeq(value)
        self._java_obj = self._java_obj.setDeploymentName(value)
        return self
    
    def setDeploymentNameCol(self, value):
        """
        Args:
            deploymentName: The name of the deployment
        """
        self._java_obj = self._java_obj.setDeploymentNameCol(value)
        return self
    
    def setDropPrompt(self, value):
        """
        Args:
            dropPrompt: whether to drop the column of prompts after templating (when using legacy models)
        """
        self._set(dropPrompt=value)
        return self
    
    def setEcho(self, value):
        """
        Args:
            echo: Echo back the prompt in addition to the completion
        """
        if isinstance(value, list):
            value = SparkContext._active_spark_context._jvm.com.microsoft.azure.synapse.ml.param.ServiceParam.toSeq(value)
        self._java_obj = self._java_obj.setEcho(value)
        return self
    
    def setEchoCol(self, value):
        """
        Args:
            echo: Echo back the prompt in addition to the completion
        """
        self._java_obj = self._java_obj.setEchoCol(value)
        return self
    
    def setErrorCol(self, value):
        """
        Args:
            errorCol: column to hold http errors
        """
        self._set(errorCol=value)
        return self
    
    def setFrequencyPenalty(self, value):
        """
        Args:
            frequencyPenalty: How much to penalize new tokens based on whether they appear in the text so far. Increases the likelihood of the model to talk about new topics.
        """
        if isinstance(value, list):
            value = SparkContext._active_spark_context._jvm.com.microsoft.azure.synapse.ml.param.ServiceParam.toSeq(value)
        self._java_obj = self._java_obj.setFrequencyPenalty(value)
        return self
    
    def setFrequencyPenaltyCol(self, value):
        """
        Args:
            frequencyPenalty: How much to penalize new tokens based on whether they appear in the text so far. Increases the likelihood of the model to talk about new topics.
        """
        self._java_obj = self._java_obj.setFrequencyPenaltyCol(value)
        return self
    
    def setLogProbs(self, value):
        """
        Args:
            logProbs: Include the log probabilities on the `logprobs` most likely tokens, as well the chosen tokens. So for example, if `logprobs` is 10, the API will return a list of the 10 most likely tokens. If `logprobs` is 0, only the chosen tokens will have logprobs returned. Minimum of 0 and maximum of 100 allowed.
        """
        if isinstance(value, list):
            value = SparkContext._active_spark_context._jvm.com.microsoft.azure.synapse.ml.param.ServiceParam.toSeq(value)
        self._java_obj = self._java_obj.setLogProbs(value)
        return self
    
    def setLogProbsCol(self, value):
        """
        Args:
            logProbs: Include the log probabilities on the `logprobs` most likely tokens, as well the chosen tokens. So for example, if `logprobs` is 10, the API will return a list of the 10 most likely tokens. If `logprobs` is 0, only the chosen tokens will have logprobs returned. Minimum of 0 and maximum of 100 allowed.
        """
        self._java_obj = self._java_obj.setLogProbsCol(value)
        return self
    
    def setMaxTokens(self, value):
        """
        Args:
            maxTokens: The maximum number of tokens to generate. Has minimum of 0.
        """
        if isinstance(value, list):
            value = SparkContext._active_spark_context._jvm.com.microsoft.azure.synapse.ml.param.ServiceParam.toSeq(value)
        self._java_obj = self._java_obj.setMaxTokens(value)
        return self
    
    def setMaxTokensCol(self, value):
        """
        Args:
            maxTokens: The maximum number of tokens to generate. Has minimum of 0.
        """
        self._java_obj = self._java_obj.setMaxTokensCol(value)
        return self
    
    def setMessagesCol(self, value):
        """
        Args:
            messagesCol: The column messages to generate chat completions for, in the chat format. This column should have type Array(Struct(role: String, content: String)).
        """
        self._set(messagesCol=value)
        return self
    
    def setN(self, value):
        """
        Args:
            n: How many snippets to generate for each prompt. Minimum of 1 and maximum of 128 allowed.
        """
        if isinstance(value, list):
            value = SparkContext._active_spark_context._jvm.com.microsoft.azure.synapse.ml.param.ServiceParam.toSeq(value)
        self._java_obj = self._java_obj.setN(value)
        return self
    
    def setNCol(self, value):
        """
        Args:
            n: How many snippets to generate for each prompt. Minimum of 1 and maximum of 128 allowed.
        """
        self._java_obj = self._java_obj.setNCol(value)
        return self
    
    def setOutputCol(self, value):
        """
        Args:
            outputCol: The name of the output column
        """
        self._set(outputCol=value)
        return self
    
    def setPostProcessing(self, value):
        """
        Args:
            postProcessing: Post processing options: csv, json, regex
        """
        self._set(postProcessing=value)
        return self
    
    def setPostProcessingOptions(self, value):
        """
        Args:
            postProcessingOptions: Options (default): delimiter=',', jsonSchema, regex, regexGroup=0
        """
        self._set(postProcessingOptions=value)
        return self
    
    def setPresencePenalty(self, value):
        """
        Args:
            presencePenalty: How much to penalize new tokens based on their existing frequency in the text so far. Decreases the likelihood of the model to repeat the same line verbatim. Has minimum of -2 and maximum of 2.
        """
        if isinstance(value, list):
            value = SparkContext._active_spark_context._jvm.com.microsoft.azure.synapse.ml.param.ServiceParam.toSeq(value)
        self._java_obj = self._java_obj.setPresencePenalty(value)
        return self
    
    def setPresencePenaltyCol(self, value):
        """
        Args:
            presencePenalty: How much to penalize new tokens based on their existing frequency in the text so far. Decreases the likelihood of the model to repeat the same line verbatim. Has minimum of -2 and maximum of 2.
        """
        self._java_obj = self._java_obj.setPresencePenaltyCol(value)
        return self
    
    def setPromptTemplate(self, value):
        """
        Args:
            promptTemplate: The prompt. supports string interpolation {col1}: {col2}.
        """
        self._set(promptTemplate=value)
        return self
    
    def setResponseFormat(self, value):
        """
        Args:
            responseFormat: Response format for the completion. Can be 'json_object' or 'text'.
        """
        if isinstance(value, list):
            value = SparkContext._active_spark_context._jvm.com.microsoft.azure.synapse.ml.param.ServiceParam.toSeq(value)
        self._java_obj = self._java_obj.setResponseFormat(value)
        return self
    
    def setResponseFormatCol(self, value):
        """
        Args:
            responseFormat: Response format for the completion. Can be 'json_object' or 'text'.
        """
        self._java_obj = self._java_obj.setResponseFormatCol(value)
        return self
    
    def setStop(self, value):
        """
        Args:
            stop: A sequence which indicates the end of the current document.
        """
        if isinstance(value, list):
            value = SparkContext._active_spark_context._jvm.com.microsoft.azure.synapse.ml.param.ServiceParam.toSeq(value)
        self._java_obj = self._java_obj.setStop(value)
        return self
    
    def setStopCol(self, value):
        """
        Args:
            stop: A sequence which indicates the end of the current document.
        """
        self._java_obj = self._java_obj.setStopCol(value)
        return self
    
    def setSubscriptionKey(self, value):
        """
        Args:
            subscriptionKey: the API key to use
        """
        if isinstance(value, list):
            value = SparkContext._active_spark_context._jvm.com.microsoft.azure.synapse.ml.param.ServiceParam.toSeq(value)
        self._java_obj = self._java_obj.setSubscriptionKey(value)
        return self
    
    def setSubscriptionKeyCol(self, value):
        """
        Args:
            subscriptionKey: the API key to use
        """
        self._java_obj = self._java_obj.setSubscriptionKeyCol(value)
        return self
    
    def setSystemPrompt(self, value):
        """
        Args:
            systemPrompt: The initial system prompt to be used.
        """
        self._set(systemPrompt=value)
        return self
    
    def setTelemHeaders(self, value):
        """
        Args:
            telemHeaders: Map of Custom Header Key-Value Tuples.
        """
        if isinstance(value, list):
            value = SparkContext._active_spark_context._jvm.com.microsoft.azure.synapse.ml.param.ServiceParam.toSeq(value)
        self._java_obj = self._java_obj.setTelemHeaders(value)
        return self
    
    def setTelemHeadersCol(self, value):
        """
        Args:
            telemHeaders: Map of Custom Header Key-Value Tuples.
        """
        self._java_obj = self._java_obj.setTelemHeadersCol(value)
        return self
    
    def setTemperature(self, value):
        """
        Args:
            temperature: What sampling temperature to use. Higher values means the model will take more risks. Try 0.9 for more creative applications, and 0 (argmax sampling) for ones with a well-defined answer. We generally recommend using this or `top_p` but not both. Minimum of 0 and maximum of 2 allowed.
        """
        if isinstance(value, list):
            value = SparkContext._active_spark_context._jvm.com.microsoft.azure.synapse.ml.param.ServiceParam.toSeq(value)
        self._java_obj = self._java_obj.setTemperature(value)
        return self
    
    def setTemperatureCol(self, value):
        """
        Args:
            temperature: What sampling temperature to use. Higher values means the model will take more risks. Try 0.9 for more creative applications, and 0 (argmax sampling) for ones with a well-defined answer. We generally recommend using this or `top_p` but not both. Minimum of 0 and maximum of 2 allowed.
        """
        self._java_obj = self._java_obj.setTemperatureCol(value)
        return self
    
    def setTimeout(self, value):
        """
        Args:
            timeout: number of seconds to wait before closing the connection
        """
        self._set(timeout=value)
        return self
    
    def setTopP(self, value):
        """
        Args:
            topP: An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10 percent probability mass are considered. We generally recommend using this or `temperature` but not both. Minimum of 0 and maximum of 1 allowed.
        """
        if isinstance(value, list):
            value = SparkContext._active_spark_context._jvm.com.microsoft.azure.synapse.ml.param.ServiceParam.toSeq(value)
        self._java_obj = self._java_obj.setTopP(value)
        return self
    
    def setTopPCol(self, value):
        """
        Args:
            topP: An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10 percent probability mass are considered. We generally recommend using this or `temperature` but not both. Minimum of 0 and maximum of 1 allowed.
        """
        self._java_obj = self._java_obj.setTopPCol(value)
        return self
    
    def setUrl(self, value):
        """
        Args:
            url: Url of the service
        """
        self._set(url=value)
        return self
    
    def setUser(self, value):
        """
        Args:
            user: The ID of the end-user, for use in tracking and rate-limiting.
        """
        if isinstance(value, list):
            value = SparkContext._active_spark_context._jvm.com.microsoft.azure.synapse.ml.param.ServiceParam.toSeq(value)
        self._java_obj = self._java_obj.setUser(value)
        return self
    
    def setUserCol(self, value):
        """
        Args:
            user: The ID of the end-user, for use in tracking and rate-limiting.
        """
        self._java_obj = self._java_obj.setUserCol(value)
        return self

    
    def getAADToken(self):
        """
        Returns:
            AADToken: AAD Token used for authentication
        """
        return self._java_obj.getAADToken()
    
    
    def getCustomAuthHeader(self):
        """
        Returns:
            CustomAuthHeader: A Custom Value for Authorization Header
        """
        return self._java_obj.getCustomAuthHeader()
    
    
    def getApiVersion(self):
        """
        Returns:
            apiVersion: version of the api
        """
        return self._java_obj.getApiVersion()
    
    
    def getBestOf(self):
        """
        Returns:
            bestOf: How many generations to create server side, and display only the best. Will not stream intermediate progress if best_of > 1. Has maximum value of 128.
        """
        return self._java_obj.getBestOf()
    
    
    def getCacheLevel(self):
        """
        Returns:
            cacheLevel: can be used to disable any server-side caching, 0=no cache, 1=prompt prefix enabled, 2=full cache
        """
        return self._java_obj.getCacheLevel()
    
    
    def getConcurrency(self):
        """
        Returns:
            concurrency: max number of concurrent calls
        """
        return self.getOrDefault(self.concurrency)
    
    
    def getConcurrentTimeout(self):
        """
        Returns:
            concurrentTimeout: max number seconds to wait on futures if concurrency >= 1
        """
        return self.getOrDefault(self.concurrentTimeout)
    
    
    def getCustomHeaders(self):
        """
        Returns:
            customHeaders: Map of Custom Header Key-Value Tuples.
        """
        return self._java_obj.getCustomHeaders()
    
    
    def getCustomUrlRoot(self):
        """
        Returns:
            customUrlRoot: The custom URL root for the service. This will not append OpenAI specific model path completions (i.e. /chat/completions) to the URL.
        """
        return self.getOrDefault(self.customUrlRoot)
    
    
    def getDeploymentName(self):
        """
        Returns:
            deploymentName: The name of the deployment
        """
        return self._java_obj.getDeploymentName()
    
    
    def getDropPrompt(self):
        """
        Returns:
            dropPrompt: whether to drop the column of prompts after templating (when using legacy models)
        """
        return self.getOrDefault(self.dropPrompt)
    
    
    def getEcho(self):
        """
        Returns:
            echo: Echo back the prompt in addition to the completion
        """
        return self._java_obj.getEcho()
    
    
    def getErrorCol(self):
        """
        Returns:
            errorCol: column to hold http errors
        """
        return self.getOrDefault(self.errorCol)
    
    
    def getFrequencyPenalty(self):
        """
        Returns:
            frequencyPenalty: How much to penalize new tokens based on whether they appear in the text so far. Increases the likelihood of the model to talk about new topics.
        """
        return self._java_obj.getFrequencyPenalty()
    
    
    def getLogProbs(self):
        """
        Returns:
            logProbs: Include the log probabilities on the `logprobs` most likely tokens, as well the chosen tokens. So for example, if `logprobs` is 10, the API will return a list of the 10 most likely tokens. If `logprobs` is 0, only the chosen tokens will have logprobs returned. Minimum of 0 and maximum of 100 allowed.
        """
        return self._java_obj.getLogProbs()
    
    
    def getMaxTokens(self):
        """
        Returns:
            maxTokens: The maximum number of tokens to generate. Has minimum of 0.
        """
        return self._java_obj.getMaxTokens()
    
    
    def getMessagesCol(self):
        """
        Returns:
            messagesCol: The column messages to generate chat completions for, in the chat format. This column should have type Array(Struct(role: String, content: String)).
        """
        return self.getOrDefault(self.messagesCol)
    
    
    def getN(self):
        """
        Returns:
            n: How many snippets to generate for each prompt. Minimum of 1 and maximum of 128 allowed.
        """
        return self._java_obj.getN()
    
    
    def getOutputCol(self):
        """
        Returns:
            outputCol: The name of the output column
        """
        return self.getOrDefault(self.outputCol)
    
    
    def getPostProcessing(self):
        """
        Returns:
            postProcessing: Post processing options: csv, json, regex
        """
        return self.getOrDefault(self.postProcessing)
    
    
    def getPostProcessingOptions(self):
        """
        Returns:
            postProcessingOptions: Options (default): delimiter=',', jsonSchema, regex, regexGroup=0
        """
        return self.getOrDefault(self.postProcessingOptions)
    
    
    def getPresencePenalty(self):
        """
        Returns:
            presencePenalty: How much to penalize new tokens based on their existing frequency in the text so far. Decreases the likelihood of the model to repeat the same line verbatim. Has minimum of -2 and maximum of 2.
        """
        return self._java_obj.getPresencePenalty()
    
    
    def getPromptTemplate(self):
        """
        Returns:
            promptTemplate: The prompt. supports string interpolation {col1}: {col2}.
        """
        return self.getOrDefault(self.promptTemplate)
    
    
    def getResponseFormat(self):
        """
        Returns:
            responseFormat: Response format for the completion. Can be 'json_object' or 'text'.
        """
        return self._java_obj.getResponseFormat()
    
    
    def getStop(self):
        """
        Returns:
            stop: A sequence which indicates the end of the current document.
        """
        return self._java_obj.getStop()
    
    
    def getSubscriptionKey(self):
        """
        Returns:
            subscriptionKey: the API key to use
        """
        return self._java_obj.getSubscriptionKey()
    
    
    def getSystemPrompt(self):
        """
        Returns:
            systemPrompt: The initial system prompt to be used.
        """
        return self.getOrDefault(self.systemPrompt)
    
    
    def getTelemHeaders(self):
        """
        Returns:
            telemHeaders: Map of Custom Header Key-Value Tuples.
        """
        return self._java_obj.getTelemHeaders()
    
    
    def getTemperature(self):
        """
        Returns:
            temperature: What sampling temperature to use. Higher values means the model will take more risks. Try 0.9 for more creative applications, and 0 (argmax sampling) for ones with a well-defined answer. We generally recommend using this or `top_p` but not both. Minimum of 0 and maximum of 2 allowed.
        """
        return self._java_obj.getTemperature()
    
    
    def getTimeout(self):
        """
        Returns:
            timeout: number of seconds to wait before closing the connection
        """
        return self.getOrDefault(self.timeout)
    
    
    def getTopP(self):
        """
        Returns:
            topP: An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10 percent probability mass are considered. We generally recommend using this or `temperature` but not both. Minimum of 0 and maximum of 1 allowed.
        """
        return self._java_obj.getTopP()
    
    
    def getUrl(self):
        """
        Returns:
            url: Url of the service
        """
        return self.getOrDefault(self.url)
    
    
    def getUser(self):
        """
        Returns:
            user: The ID of the end-user, for use in tracking and rate-limiting.
        """
        return self._java_obj.getUser()

    

    def setCustomServiceName(self, value):
        self._java_obj = self._java_obj.setCustomServiceName(value)
        return self
    
    def setEndpoint(self, value):
        self._java_obj = self._java_obj.setEndpoint(value)
        return self
    
    def setDefaultInternalEndpoint(self, value):
        self._java_obj = self._java_obj.setDefaultInternalEndpoint(value)
        return self
    
    def _transform(self, dataset: DataFrame) -> DataFrame:
        return super()._transform(dataset)
        