using Accent.API.Services;
using Microsoft.AspNetCore.Mvc;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Accent.API.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class AccentController : Controller
    {
        private readonly IAccentService _accentService;
        public AccentController(IAccentService accentService)
        {
            _accentService = accentService;
        }

        [HttpGet("convert/{text}")]
        public IActionResult Convert(string text)
        {
            string result = _accentService.GetResult(text);
            return Ok(new { result = result });
        }
    }
}
