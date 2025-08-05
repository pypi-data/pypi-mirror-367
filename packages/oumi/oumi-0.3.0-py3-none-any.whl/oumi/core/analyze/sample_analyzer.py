# Copyright 2025 - Oumi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Base classes for sample analyzer plugins."""

from abc import ABC, abstractmethod
from typing import Any, Optional


class SampleAnalyzer(ABC):
    """Base class for sample analyzer plugins that analyze individual samples."""

    @abstractmethod
    def analyze_message(
        self, text_content: str, tokenizer: Optional[Any] = None
    ) -> dict[str, Any]:
        """Analyze a single message and return metrics.

        Args:
            text_content: The text content to analyze
            tokenizer: Optional tokenizer to use for tokenization-based analysis

        Returns:
            Dictionary containing analysis metrics
        """
        pass
