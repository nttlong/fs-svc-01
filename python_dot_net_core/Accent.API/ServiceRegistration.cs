using Accent.API.Services;
using Accent.Utils;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading.Tasks;

namespace Accent.API
{
    public static class ServiceRegistration
    {
        public static void AddAccentService(this IServiceCollection services, IConfiguration configuration)
        {
            // Lấy đường dẫn folder Datasets_Training_Accent trong appsetting.json
            string baseFolderPath = configuration["AccentTrainingDataPath"];
            if (!Directory.Exists(baseFolderPath)) throw new Exception($"Could not found folder path \"Datasets_Training_Accent\"");

            // Khởi tạo model
            services.AddSingleton<AccentPredictor>(
                new AccentPredictor(
                    gram1Path: baseFolderPath + "news1gram",
                    gram2Path: baseFolderPath + "news2grams",
                    statisticPath: baseFolderPath + "_1Statistic",
                    replaceSpecialPath: baseFolderPath + "ReplaceSpecial.txt")
            );

            // Khởi tạo service
            services.AddSingleton<IAccentService, AccentService>();
        }
    }
}
