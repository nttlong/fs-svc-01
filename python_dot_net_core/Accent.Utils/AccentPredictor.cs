using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Accent.KShortestPaths.Model;
using Accent.KShortestPaths.Model.Abstracts;
using Accent.KShortestPaths.Common;
using Accent.Utils;
using System.IO;
using System.Text.RegularExpressions;
using Accent.KShortestPaths.Controller;
using System;
using static System.Net.Mime.MediaTypeNames;
using System.Threading;
using System.Xml;
using System.Configuration;
using System.Diagnostics;

namespace Accent.Utils
{
    public class AccentPredictor
    {
        private static Dictionary<string, int> _1Gram = new Dictionary<string, int>();
        private static Dictionary<string, int> _2Grams = new Dictionary<string, int>();
        private static Dictionary<string, int> _1Statistic = new Dictionary<string, int>();
        private HashSet<string> _accents;
        private static long _size1Gram = 216448;//0;
        private static long _totalCount1Gram = 400508609;//0;
        private int _maxWordLength = 8;
        int maxp = 100;
        private static long _size2Grams = 5553699;// 0;
        private static long _totalCount2Grams = 400508022;//0;
        private HashSet<string> _globalPosibleChanges = new HashSet<string>();
        private static string _replaceSpecialPath;

        public double MIN = -1000;

        /// <summary>
        /// Ngram bóc tách theo cụm từ theo từng đơn vị theo khoảng trắng
        /// 1Ngram : tách 1 từ
        /// 2Ngram: tách 2 từ
        /// replaceSpecialPath: tùy chỉnh thay thế từ không hợp lý
        /// </summary>
        /// <param name="gram1Path"></param>
        /// <param name="gram2Path"></param>
        /// <param name="statisticPath"></param>
        /// <param name="replaceSpecialPath"></param>
        public AccentPredictor(string gram1Path, string gram2Path, string statisticPath, string replaceSpecialPath)
        {
            Console.WriteLine("Loading NGrams...");
            Console.WriteLine(DateTime.Now);

            Stopwatch stopWatch = new Stopwatch();
            stopWatch.Start();

            _replaceSpecialPath = replaceSpecialPath;
            LoadNGram(gram1Path, gram2Path, statisticPath);

            stopWatch.Stop();

            Console.WriteLine($"Time taken: {stopWatch.Elapsed.ToString(@"m\:ss\.fff")}");
            Console.WriteLine("Done!");
        }

        public virtual void LoadNGram(string gram1Path, string gram2Path, string statisticPath)
        {
            _accents = GetAccentInfo();
            _1Statistic = GetNGram1Statistic(statisticPath);
            _1Gram = GetNgrams(gram1Path, true);
            _2Grams = GetNgrams(gram2Path, true);
        }

        public virtual void GetPosibleChanges(string input, int index, HashSet<string> posibleChanges)
        {
            if (input.Length > _maxWordLength)
            {
                return;
            }
            if (index > input.Length)
            {
                return;
            }
            else if (index == input.Length)
            {

                if (_1Gram.ContainsKey(input))
                {
                    _globalPosibleChanges.Add(input);
                }
                return;
            }
            char[] charSeq = input.ToCharArray();
            bool check = false;
            foreach (string s in posibleChanges)
            {

                if (s.IndexOf(charSeq[index]) != -1)
                {
                    for (int i = 0; i < s.Length; i++)
                    {
                        char[] tmp = input.ToCharArray();
                        tmp[index] = s[i];
                        string sTmp = "";
                        for (int j = 0; j < input.Length; j++)
                        {
                            sTmp += tmp[j] + "";
                        }

                        GetPosibleChanges(sTmp, index + 1, posibleChanges);
                    }
                    check = true;
                }

            }
            if (!check)
            {
                GetPosibleChanges(input, index + 1, posibleChanges);
            }
        }

        /// <summary>
        /// Load dữ liệu từ, cụm từ đã được tranning.
        /// </summary>
        /// <param name="fileIn"></param>
        /// <param name="is1Gram"></param>
        /// <returns></returns>
        public static Dictionary<string, int> GetNgrams(string fileIn, bool is1Gram)
        {
            Dictionary<string, int> ngrams = new Dictionary<string, int>();

            // Nên lưu chổ này lại qua file binary để load cho nhanh,
            // Java - ngrams.put(ngramWord, ngramCount); C# ngrams.Add

            #region Tải dữ liệu Ngram
            // Đã ghi Dictionary 1ngrams và 2ngrams vào file binary để tăng tốc độ,
            //thay thế code bên dưới phải tính lại từ đầu.

            //long size = 0, counts = 0;
            //try
            //{

            //    var file = new FileInfo(fileIn);
            //    var content = File.ReadAllLines(file.FullName, Encoding.UTF8);

            //    string line = "";
            //    for (int i = 0; i < content.Length; i++)
            //    {
            //        line = content[i];

            //        int indexSpace = line.LastIndexOf(' ');
            //        int indexTab = line.LastIndexOf('\t');

            //        if (indexTab < indexSpace)
            //        {
            //            indexTab = indexSpace;
            //        }
            //        string ngramWord = line.Substring(0, indexTab);
            //        if (!is1Gram)
            //        {
            //            string firstGram = ngramWord.Substring(0, ngramWord.IndexOf(' '));
            //            if (_1Statistic.ContainsKey(firstGram))
            //            {
            //                int val = _1Statistic[firstGram];
            //                _1Statistic[firstGram] = val + 1;
            //            }
            //            else
            //            {
            //                _1Statistic.Add(firstGram, 1);
            //            }
            //        }
            //        size++;
            //        int ngramCount = int.Parse(line.Substring(indexTab + 1));
            //        counts += ngramCount;

            //        //ngrams.Add(ngramWord, ngramCount);

            //        // Java - ngrams.put(ngramWord, ngramCount);
            //        // put - nếu có rồi thì update không thì thêm vào

            //        // C#
            //        if (ngrams.ContainsKey(ngramWord))
            //        {
            //            ngrams[ngramWord] = ngramCount;
            //            //ngrams.Add(ngramWord + " ", ngramCount);
            //        }
            //        else
            //        {
            //            ngrams.Add(ngramWord, ngramCount);
            //        }
            //    }
            //}
            //catch (Exception ex)
            //{

            //}
            //if (is1Gram)
            //{
            //    _size1Gram = size;
            //    _totalCount1Gram = counts;
            //}
            //else
            //{
            //    _size2Grams = size;
            //    _totalCount2Grams = counts;
            //}
            #endregion

            using (FileStream fs = new FileStream(fileIn, FileMode.Open, FileAccess.Read))
            {
                using (BinaryReader reader = new BinaryReader(fs))
                {
                    int count = reader.ReadInt32();
                    for (int i = 0; i < count; i++)
                    {
                        ngrams.Add(reader.ReadString(), reader.ReadInt32());
                    }
                }
            }

            return ngrams;

        }
        public static Dictionary<string, int> GetNGram1Statistic(string fileIn)
        {
            Dictionary<string, int> ngrams = new Dictionary<string, int>();

            using (FileStream fs = new FileStream(fileIn, FileMode.Open, FileAccess.Read))
            {
                using (StreamReader sr = new StreamReader(fs))
                {
                    while (!sr.EndOfStream)
                    {
                        string line = sr.ReadLine();

                        int indexSpace = line.LastIndexOf(' ');
                        int indexTab = line.LastIndexOf('\t');

                        if (indexTab < indexSpace)
                        {
                            indexTab = indexSpace;
                        }
                        string ngramWord = line.Substring(0, indexTab);
                        int ngramCount = int.Parse(line.Substring(indexTab + 1));
                        ngrams.Add(ngramWord, ngramCount);
                    }
                }
            }
            return ngrams;
        }

        public virtual HashSet<string> GetAccentInfo()
        {
            HashSet<string> output = new HashSet<string>();
            string[] accent = new string[]
                {
                "UÙÚỦỤŨƯỪỨỬỰỮ",
                "eèéẻẹẽêềếểệễ",
                "oòóỏọõôồốổộỗơờớởợỡ",
                "OÒÓỎỌÕÔỒỐỔỘỖƠỜỚỞỢỠ",
                "uùúủụũưừứửựữ",
                "DĐ",
                "aàáảạãâầấẩậẫăằắẳặẵ",
                "dđ",
                "AÀÁẢẠÃÂẦẤẨẬẪĂẰẮẲẶẴ",
                "iìíỉịĩ",
                "EÈÉẺẸẼÊỀẾỂỆỄ",
                "YỲÝỶỴỸ",
                "IÌÍỈỊĨ",
                "yỳýỷỵỹ",
                };
            foreach (var item in accent)
            {
                output.Add(item);
            }
            return output;
        }

        public virtual HashSet<string> GetVocab(string fileIn)
        {
            HashSet<string> output = new HashSet<string>();
            StreamReader fis = null;
            try
            {
                fis = File.OpenText(fileIn);
                string line = "";
                while ((line = fis.ReadLine()) != null)
                {
                    line = fis.ReadLine();
                    if (!String.IsNullOrEmpty(line))
                    {
                        output.Add(Regex.Split(line, "\\s+")[0]);
                    }
                }
            }
            catch (IOException)
            {
            }
            return output;
        }
        public virtual int GetGramCount(string ngramWord, Dictionary<string, int> ngrams)
        {
            if (!ngrams.ContainsKey(ngramWord))
            {
                return 0;
            }
            int output = ngrams[ngramWord];
            return output;
        }

        public virtual void SetPosibleChanges()
        {
            _globalPosibleChanges.Clear();
            _globalPosibleChanges = new HashSet<string>();
        }

        public string PredictAccentsWithMultiMatches(string sentence, int nResults, bool getWeight = true)
        {
            LinkedHashMap<string, double> output = new LinkedHashMap<string, double>();
            string @in = Utils.normaliseString(sentence);
            string lowercaseIn = @in.ToLower();
            string[] words = ("0 " + lowercaseIn + " 0").Split(' ');
            Graph graph = new VariableGraph();
            Dictionary<int, string> idxWordMap = new Dictionary<int, string>();
            int index = 0;
            int[] numberP = new int[words.Length];

            string[,] possibleChange = new string[words.Length, maxp];

            int[,] indices = new int[words.Length, maxp];
            int nVertex = 0;

            index = BuildGraph(words, graph, idxWordMap, index, numberP, possibleChange, indices, nVertex);

            //Yen Algorithm for kShortestPaths
            YenTopKShortestPathsAlg yenAlg = new YenTopKShortestPathsAlg(graph);
            List<Accent.KShortestPaths.Model.Path> shortest_paths_list = yenAlg.get_shortest_paths(graph.get_vertex(0), graph.get_vertex(index - 1), nResults);
            foreach (Accent.KShortestPaths.Model.Path path in shortest_paths_list)
            {
                List<BaseVertex> pathVertex = path.get_vertices();
                string text = "";
                for (int i = 1; i < pathVertex.Count - 1; i++)
                {
                    BaseVertex vertext = pathVertex[i];
                    text += idxWordMap[vertext.get_id()] + " ";                   
                }
                text = ReplaceSpecial(text);
                output.Add(ProcessOutput(@in, text.Trim()), path.get_weight());
            }

            // Không lấy trọng số đo lường cho các trường hợp thêm dấu.
            if (!getWeight)
                return output.ToString2();

            return output.ToString();
        }

        private int BuildGraph(string[] words, Graph graph, Dictionary<int, string> idxWordMap, int index, int[] numberP, string[,] possibleChange, int[,] indices, int nVertex)
        {

            for (int i = 0; i < words.Length; i++)
            {
                _globalPosibleChanges = new HashSet<string>();
                GetPosibleChanges(words[i], 0, _accents);
                if (_globalPosibleChanges.Count() == 0)
                {
                    _globalPosibleChanges.Add(words[i]);
                }
                numberP[i] = _globalPosibleChanges.Count();
                nVertex += numberP[i];

                for (int y = 0; y < numberP[i]; y++)
                {
                    possibleChange[i, y] = _globalPosibleChanges.ToArray()[y];
                }

                for (int j = 0; j < numberP[i]; j++)
                {
                    idxWordMap[index] = possibleChange[i, j];
                    indices[i, j] = index++;
                }
            }
            graph.initGraph(nVertex);
            for (int i = 1; i < words.Length; i++)
            {
                int recentPossibleNum = numberP[i];
                int oldPossibleNum = numberP[i - 1];

                for (int j = 0; j < recentPossibleNum; j++)
                {
                    for (int k = 0; k < oldPossibleNum; k++)
                    {
                        string _new = possibleChange[i, j];
                        string _old = possibleChange[i - 1, k];
                        int currentVertex = indices[i, j];
                        int previousVertex = indices[i - 1, k];
                        double log = -100.0;
                        int number2GRam = GetGramCount(_old + " " + _new, _2Grams);
                        int number1GRam = GetGramCount(_old, _1Gram);
                        if (number1GRam > 0 && number2GRam > 0)
                        {
                            log = Math.Log((double)(number2GRam + 1) / (number1GRam + _1Statistic[_old]));
                        }
                        else
                        {
                            log = Math.Log(1.0 / (2 * (_size2Grams + _totalCount2Grams)));
                        }

                        if (i == 2)
                        {
                            log += Math.Log((double)(number1GRam + 1) / (_size1Gram + _totalCount1Gram));
                        }
                        graph.add_edge(previousVertex, currentVertex, -log);

                    }
                }
            }
            return index;
        }

        //Using Dijkstra shortest path alg --> return online the best match: optimised for speed
        /// <summary>
        /// Lấy nội dung có dấu.
        /// </summary>
        /// <param name="inputContent"></param>
        /// <returns></returns>
        public string PredictAccents(string inputContent)
        {
            string[] inputSentence = Regex.Split(inputContent, "[\\.\\!\\,\n\\;\\?]");
            StringBuilder output = new StringBuilder();
            foreach (string input in inputSentence)
            {
                SetPosibleChanges();
                string @in = Utils.normaliseString(input);
                string lowercaseIn = @in.ToLower();
                string[] words = lowercaseIn.Split(' ');
                int[] numberP = new int[words.Length];
                int[,] trace = new int[words.Length, maxp];
                double[,] Q = new double[words.Length, maxp];
                string[,] possibleChange = new string[words.Length, maxp];
                for (int i = 0; i < words.Length; i++)
                {
                    _globalPosibleChanges = new HashSet<string>();
                    GetPosibleChanges(words[i], 0, _accents);
                    if (_globalPosibleChanges.Count() == 0)
                    {
                        _globalPosibleChanges.Add(words[i]);
                    }
                    numberP[i] = _globalPosibleChanges.Count();


                    // cách cũ lấy 1 đơn vị
                    //obj1D = (possibleChange).Cast<string>().ToArray();
                    //_globalPosibleChanges.CopyTo(obj1D, i);

                    //_globalPosibleChanges.CopyTo((possibleChange).Cast<string>().ToArray(), i);
                    //possibleChange.SetValue(_globalPosibleChanges.ToArray()[i].ToString(), i);
                    // _globalPosibleChanges.CopyTo((possibleChange).Cast<string>().ToArray(), i);
                    //possibleChange = SingleToMulti(obj1D.Where(c => c != null).ToArray(), i);
                    //_globalPosibleChanges.CopyTo(obj1D, i);
                    //int sqrt = obj1D.Where(c => c != null).ToArray().Length;//array.Length;

                    for (int y = 0; y < numberP[i]; y++)
                    {
                        possibleChange[i, y] = _globalPosibleChanges.ToArray()[y];
                    }
                }


                for (int i = 0; i < words.Length; i++)
                {
                    for (int j = 0; j < maxp; j++)
                    {
                        trace[i, j] = 0;
                    }
                }

                for (int i = 0; i < numberP[0]; i++)
                {
                    Q[0, i] = 0.0;
                }

                if (words.Length == 1)
                {
                    int max = 0;
                    string sure = words[0];
                    for (int i = 0; i < numberP[0]; i++)
                    {
                        string possible = possibleChange[0, i]; //obj1D[i].ToString();//
                        int number1GRam = GetGramCount(possible, _1Gram);
                        if (max < number1GRam)
                        {
                            max = number1GRam;
                            sure = possible;
                        }
                    }
                    output.Append(sure.Trim() + "\n");
                }
                else
                {
                    for (int i1 = 1; i1 < words.Length; i1++)
                    {
                        int recentPossibleNum = numberP[i1];
                        int oldPossibleNum = numberP[i1 - 1];
                        for (int j = 0; j < recentPossibleNum; j++)
                        {
                            Q[i1, j] = MIN;
                            double temp = MIN;
                            for (int k1 = 0; k1 < oldPossibleNum; k1++)
                            {
                                string _new = possibleChange[i1, j];
                                string _old = possibleChange[i1 - 1, k1];
                                double log = -100.0;
                                int number2GRam = GetGramCount(_old + " " + _new, _2Grams);
                                int number1GRam = GetGramCount(_old, _1Gram);
                                if (number1GRam > 0 && number2GRam > 0)
                                {
                                    log = Math.Log((double)(number2GRam + 1) / (number1GRam + _1Statistic[_old]));
                                }
                                else
                                {
                                    log = Math.Log(1.0 / (2 * (_size2Grams + _totalCount2Grams)));
                                }

                                if (i1 == 1)
                                {
                                    log += Math.Log((double)(number1GRam + 1) / (_size1Gram + _totalCount1Gram));
                                }
                                if (temp != Q[i1 - 1, k1])
                                {
                                    if (temp == MIN)
                                    {
                                        temp = Q[i1 - 1, k1];
                                    }
                                }
                                double value = Q[i1 - 1, k1] + log;

                                if (Q[i1, j] < value)
                                {

                                    Q[i1, j] = value;
                                    trace[i1, j] = k1;
                                }
                            }
                        }
                    }
                    double max = MIN;
                    int k = 0;
                    for (int l = 0; l < numberP[words.Length - 1]; l++)
                    {
                        if (max <= Q[words.Length - 1, l])
                        {
                            max = Q[words.Length - 1, l];
                            k = l;
                        }
                    }
                    string result = possibleChange[words.Length - 1, k];
                    k = trace[words.Length - 1, k];
                    int i = words.Length - 2;
                    while (i >= 0)
                    {
                        result = possibleChange[i, k] + " " + result;
                        k = trace[i--, k];
                    }
                    output.Append(ProcessOutput(@in, result).Trim() + "\n");

                }
            }
            string resultOutput = output.ToString();
            resultOutput = ReplaceSpecial(resultOutput);
            return resultOutput.Trim();
        }

        private string ReplaceSpecial(string text)
        {
            if (String.IsNullOrEmpty(text))
                return "";

            var listWordInCorrect = new Dictionary<string, string>();

            var file = new FileInfo(_replaceSpecialPath);
            var words = File.ReadAllLines(file.FullName, Encoding.UTF8);


            for (int i = 0; i < words.Length; i++)
            {
                var line = words[i].Split('\t');
                listWordInCorrect.Add(line[0], line[1]);
            }

            foreach (KeyValuePair<string, string> replacement in listWordInCorrect)
            {
                text = Regex.Replace(text, replacement.Key, replacement.Value);
            }

            return text;
        }

        private string ProcessOutput(string input, string output)
        {

            StringBuilder str = new StringBuilder();

            for (int i = 0; i < input.Length; i++)
            {
                char inputChar = input[i];
                char outputChar = ' ';
                if (i < output.Length)
                {
                    outputChar = output[i];
                }


                if (char.IsUpper(inputChar))
                {
                    str.Append(char.ToUpper(outputChar));
                }
                else
                {
                    str.Append(outputChar);
                }
            }
            return str.ToString();
        }


        public double GetAccuracy(string fileIn)
        {
            FileProcessor fp = new FileProcessor();
            var file = new FileInfo(fileIn);

            var input = File.ReadAllText(file.FullName, Encoding.UTF8);

            //string input = fp.readFileNew(fileIn);
            input = Utils.normaliseString(input);
            string[] inputSentence = Regex.Split(input, "[\\.\\!\\,\n\\;\\?]"); //input.Split('.', '!', ',', '\n', ';', '?');
            string clearSign = CompareString.getUnsignedString(input).Trim();
            DateTime start = new DateTime();
            string @out = PredictAccents(clearSign.Trim());
            double processedTime = (DateTime.Now.Millisecond - start.Millisecond) * 1.0 / 1000;
            Console.WriteLine("Processed time: " + processedTime + " seconds");
            string[] output = Regex.Split(@out, "\n");// @out.Split('\n');
            Console.WriteLine("Speed: " + output.Length * 1.0 / processedTime + " sents/second");
            Console.WriteLine("Speed: " + Regex.Split(@out, "\\s+").Length * 1.0 / processedTime + " words/second");
            int countAll = 1;
            int countMatch = 0;

            for (int i = 0; i < inputSentence.Length; i++)
            {

                if (i < output.Length)
                {
                    string[] wordsIn = Utils.normaliseString(inputSentence[i]).Trim().Split(' ');
                    string[] wordsOut = output[i].Trim().Split(' ');
                    bool shouldPrint = false;
                    if (wordsIn.Length == wordsOut.Length)
                    {
                        for (int j = 0; j < wordsOut.Length; j++)
                        {
                            if (wordsIn[j].Trim().Equals(wordsOut[j].Trim(), StringComparison.OrdinalIgnoreCase))
                            {
                                countMatch++;
                            }
                            else
                            {
                                shouldPrint = true;
                            }
                            countAll++;
                        }
                    }

                    if (shouldPrint)
                    {
                        Console.WriteLine("input: " + inputSentence[i]);
                        Console.WriteLine("output: " + output[i]);
                    }
                }
            }
            Console.WriteLine("Correct:" + countMatch);
            Console.WriteLine("All:" + countAll);

            return (double)(countMatch * 100) / countAll;
        }
    }
}
