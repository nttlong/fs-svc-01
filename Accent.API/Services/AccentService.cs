using Accent.Utils;
using Microsoft.Extensions.Configuration;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
using System.Threading.Tasks;

namespace Accent.API.Services
{
    public class AccentService : IAccentService
    {
        private readonly AccentPredictor _accent;
        public AccentService(AccentPredictor accent)
        {
            _accent = accent;
        }

        public string GetResult(string text)
        {
            string result = _accent.PredictAccents(text);
            if (!String.IsNullOrEmpty(result))
                result = Regex.Replace(result, @"\n", " ");

            return result;
        }
    }
}
