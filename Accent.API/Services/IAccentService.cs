using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Accent.API.Services
{
    public interface IAccentService
    {
        string GetResult(string text);
    }
}
