#include <cmath>
#include <iostream>
#include <unistd.h>


namespace math {
    /**
     * Absolute value
     */
    inline float absolute(float x) {
        return x >= 0 ? x : -x;
    }

    /**
     * Alias of max
     */
    inline float largest(float x, float y) {
        return x > y ? x : y;
    }

    /**
     * Alias of min
     */
    inline float least(float x, float y) {
        return x < y ? x : y;
    }

    /**
     * Square root (absolute value)
     */
    inline float sqrt(float x) {
        return std::sqrt(math::absolute(x));
    }

    /**
     * Division (0 safe)
     */
    inline float divide(float n, float d) {
        return math::absolute(d) > 0.000001 ? n / d : n;
    }

    /**
     * Log(1 + abs(x))
     */
    inline float log(float x) {
        return std::log(1 + math::absolute(x));
    }

    /**
     * Exp(abs(x)) with x <= 30
     */
    inline float exp(float x) {
        return math::absolute(x) <= 30 ? std::exp(math::absolute(x)) : 0;
    }
}
namespace np {
    /**
     * Array mean
     */
    float mean(float *array, const uint16_t count) {
        float sum = 0;

        for (uint16_t i = 0; i < count; i++)
            sum += array[i];

        return sum / count;
    }

    /**
     * Array abs mean
     */
    float absmean(float *array, const uint16_t count) {
        float sum = 0;

        for (uint16_t i = 0; i < count; i++)
            sum += abs(array[i]);

        return sum / count;
    }

    /**
     * Array maximum
     */
    float maximum(float *array, const uint16_t count) {
        float maximum = array[0];

        for (uint16_t i = 1; i < count; i++)
            if (array[i] > maximum)
                maximum = array[i];

        return maximum;
    }

    /**
     * Array minimum
     */
    float minimum(float *array, const uint16_t count) {
        float minimum = array[0];

        for (uint16_t i = 1; i < count; i++)
            if (array[i] < minimum)
                minimum = array[i];

        return minimum;
    }
}


// pre-processing chain
namespace internals {
    #pragma once
#include <cstring>

namespace math {
    /**
     * Absolute value
     */
    inline float absolute(float x) {
        return x >= 0 ? x : -x;
    }

    /**
     * Alias of max
     */
    inline float largest(float x, float y) {
        return x > y ? x : y;
    }

    /**
     * Alias of min
     */
    inline float least(float x, float y) {
        return x < y ? x : y;
    }

    /**
     * Square root (absolute value)
     */
    inline float sqrt(float x) {
        return std::sqrt(math::absolute(x));
    }

    /**
     * Division (0 safe)
     */
    inline float divide(float n, float d) {
        return math::absolute(d) > 0.000001 ? n / d : n;
    }

    /**
     * Log(1 + abs(x))
     */
    inline float log(float x) {
        return std::log(1 + math::absolute(x));
    }

    /**
     * Exp(abs(x)) with x <= 30
     */
    inline float exp(float x) {
        return math::absolute(x) <= 30 ? std::exp(math::absolute(x)) : 0;
    }
}

/**
 * A classification chain for tabular data
 */
namespace tinyml4all {
    /**
 * Handle all inputs of the chain
 * (from outside and internal)
 */
class Input {
    public:
        
            float _PSawsX__mx;
        
            float _aGTzid__my;
        
            float _Tz3Q7P__mz;
        

        /**
         * Copy from other input
         */
        void copyFrom(Input& other) {
            
                _PSawsX__mx = other._PSawsX__mx;
            
                _aGTzid__my = other._aGTzid__my;
            
                _Tz3Q7P__mz = other._Tz3Q7P__mz;
            
        }
};
    /**
 * Handle all outputs
 * TODO
 */
 class Output {
    public:
        struct {
            float value;
        } regression;
        struct {
            uint8_t idx;
            uint8_t prevIdx;
            float confidence;
            float prevConfidence;
            String label;
            String prevLabel;
        } classification;

        Output() {
            classification.idx = 0;
            classification.confidence = 0;
        }
 };
    class Classmap {
    public:

        /**
         * Get label for index
         */
        String get(int8_t idx) {
            
                switch (idx) {
                    
                        case 0: return "next";
                    
                        case 1: return "raise";
                    
                        case 2: return "tap";
                    
                    default: return "Unknown";
                }
            

            return String(idx);
        }
};

    // processing blocks
    
    /**
 * Scale(method=minmax, offsets=[-400. -400. -400.], scales=[799.987793 709.49707  799.987793])
 */
class _ctReKH__scale_135010439616208_8438152476013 {
    public:

        void operator()(Input& input, Output& output) {
            

            
                
                    input._PSawsX__mx = (input._PSawsX__mx - -400.0f) * 0.0012500190737285413f;
                
                    input._aGTzid__my = (input._aGTzid__my - -400.0f) * 0.0014094490904662932f;
                
                    input._Tz3Q7P__mz = (input._Tz3Q7P__mz - -400.0f) * 0.0012500190737285413f;
                
            

            
        }

        /**
         * Always ready
         */
        bool isReady() {
            return true;
        }
};
    

    /**
     * Chain class
     * Chain(blocks=[Scale(method=minmax, offsets=[-400. -400. -400.], scales=[799.987793 709.49707  799.987793])])
     */
     class PreprocessingChain {
        public:
            Input input;
            Output output;
            Classmap classmap;

            /**
 * Transform Input
 */
bool operator()(const Input& input) {
    return operator()(input._PSawsX__mx, input._aGTzid__my, input._Tz3Q7P__mz);
}

/**
 * Transform array input
 */
bool operator()(float *inputs) {
    return operator()(inputs[0], inputs[1], inputs[2]);
}

/**
 * Transform const array input
 */
bool operator()(const float *inputs) {
    return operator()(inputs[0], inputs[1], inputs[2]);
}

            /**
             * Transform variadic input
             */
            bool operator()(const float _PSawsX__mx, const float _aGTzid__my, const float _Tz3Q7P__mz) {
                // assign variables to input
                
                    input._PSawsX__mx = _PSawsX__mx;
                
                    input._aGTzid__my = _aGTzid__my;
                
                    input._Tz3Q7P__mz = _Tz3Q7P__mz;
                

                // run blocks
                
                    // Scale(method=minmax, offsets=[-400. -400. -400.], scales=[799.987793 709.49707  799.987793])
                    block1(input, output);

                    if (!block1.isReady())
                        return false;
                

                output.classification.label = classmap.get(output.classification.idx);

                return true;
            }

        protected:
            
                // Scale(method=minmax, offsets=[-400. -400. -400.], scales=[799.987793 709.49707  799.987793])
                _ctReKH__scale_135010439616208_8438152476013 block1;
            
    };
}
}


namespace tinyml4all {
    /**
 * Handle all inputs of the chain
 * (from outside and internal)
 */
class Input {
    public:
        
            float _EklLmr__momentsmaxmz;
        
            float _fz7hE5__count_above_meanmy;
        
            float _jSiICE__momentsmeanmx;
        
            float _FkO1dy__momentsmeanmy;
        
            float _F5bOdo__momentsstdmy;
        
            float _SalQct__momentsminmy;
        
            float _kIX8Zh__momentsmaxmx;
        
            float _9XogdU__autocorrelationmx;
        
            float _Tz3Q7P__mz;
        
            float _V7ILZq__count_above_meanmz;
        
            float _zZmGqV__count_above_meanmx;
        
            float _u0yBgY__autocorrelationmz;
        
            float _vI9LHD__momentsstdmx;
        
            float _15tt2v__momentsmeanabsmz;
        
            float _jWd98P__peaksmx;
        
            float _x2BxiN__momentsmeanabsmy;
        
            float _ypwfnt__momentsmaxabsmx;
        
            float _PSawsX__mx;
        
            float _Znwbtu__momentsstdmz;
        
            float _clg7v2__momentsmaxabsmz;
        
            float _km4spH__peaksmz;
        
            float _082CHh__momentsminmz;
        
            float _aGTzid__my;
        
            float _hqsjUF__momentsmeanmz;
        
            float _XiOuCe__momentsminmx;
        
            float _Oic8kL__momentsminabsmy;
        
            float _HRgdF2__momentsmaxmy;
        
            float _lnNby7__momentsmeanabsmx;
        
            float _SxHu89__momentsmaxabsmy;
        
            float _ZP45RY__peaksmy;
        
            float _b2Fi2p__momentsminabsmz;
        
            float _j861DZ__autocorrelationmy;
        
            float _IknBSj__momentsminabsmx;
        

        /**
         * Copy from other input
         */
        void copyFrom(Input& other) {
            
                _EklLmr__momentsmaxmz = other._EklLmr__momentsmaxmz;
            
                _fz7hE5__count_above_meanmy = other._fz7hE5__count_above_meanmy;
            
                _jSiICE__momentsmeanmx = other._jSiICE__momentsmeanmx;
            
                _FkO1dy__momentsmeanmy = other._FkO1dy__momentsmeanmy;
            
                _F5bOdo__momentsstdmy = other._F5bOdo__momentsstdmy;
            
                _SalQct__momentsminmy = other._SalQct__momentsminmy;
            
                _kIX8Zh__momentsmaxmx = other._kIX8Zh__momentsmaxmx;
            
                _9XogdU__autocorrelationmx = other._9XogdU__autocorrelationmx;
            
                _Tz3Q7P__mz = other._Tz3Q7P__mz;
            
                _V7ILZq__count_above_meanmz = other._V7ILZq__count_above_meanmz;
            
                _zZmGqV__count_above_meanmx = other._zZmGqV__count_above_meanmx;
            
                _u0yBgY__autocorrelationmz = other._u0yBgY__autocorrelationmz;
            
                _vI9LHD__momentsstdmx = other._vI9LHD__momentsstdmx;
            
                _15tt2v__momentsmeanabsmz = other._15tt2v__momentsmeanabsmz;
            
                _jWd98P__peaksmx = other._jWd98P__peaksmx;
            
                _x2BxiN__momentsmeanabsmy = other._x2BxiN__momentsmeanabsmy;
            
                _ypwfnt__momentsmaxabsmx = other._ypwfnt__momentsmaxabsmx;
            
                _PSawsX__mx = other._PSawsX__mx;
            
                _Znwbtu__momentsstdmz = other._Znwbtu__momentsstdmz;
            
                _clg7v2__momentsmaxabsmz = other._clg7v2__momentsmaxabsmz;
            
                _km4spH__peaksmz = other._km4spH__peaksmz;
            
                _082CHh__momentsminmz = other._082CHh__momentsminmz;
            
                _aGTzid__my = other._aGTzid__my;
            
                _hqsjUF__momentsmeanmz = other._hqsjUF__momentsmeanmz;
            
                _XiOuCe__momentsminmx = other._XiOuCe__momentsminmx;
            
                _Oic8kL__momentsminabsmy = other._Oic8kL__momentsminabsmy;
            
                _HRgdF2__momentsmaxmy = other._HRgdF2__momentsmaxmy;
            
                _lnNby7__momentsmeanabsmx = other._lnNby7__momentsmeanabsmx;
            
                _SxHu89__momentsmaxabsmy = other._SxHu89__momentsmaxabsmy;
            
                _ZP45RY__peaksmy = other._ZP45RY__peaksmy;
            
                _b2Fi2p__momentsminabsmz = other._b2Fi2p__momentsminabsmz;
            
                _j861DZ__autocorrelationmy = other._j861DZ__autocorrelationmy;
            
                _IknBSj__momentsminabsmx = other._IknBSj__momentsminabsmx;
            
        }
};
    /**
 * Handle all outputs
 * TODO
 */
 class Output {
    public:
        struct {
            float value;
        } regression;
        struct {
            uint8_t idx;
            uint8_t prevIdx;
            float confidence;
            float prevConfidence;
            String label;
            String prevLabel;
        } classification;

        Output() {
            classification.idx = 0;
            classification.confidence = 0;
        }
 };
    class Classmap {
    public:

        /**
         * Get label for index
         */
        String get(int8_t idx) {
            
                switch (idx) {
                    
                        case 0: return "next";
                    
                        case 1: return "raise";
                    
                        case 2: return "tap";
                    
                    default: return "Unknown";
                }
            

            return String(idx);
        }
};

    // windowing
    class Window {
    public:
        const uint16_t length = 76;
        float data[3][76];

        /**
         * Constructor
         */
        Window() : head(0) {
        }

        /**
         * Feed data
         */
        void operator()(Input& input) {
            if (isReady())
                shift();

            
                data[0][head] = input._PSawsX__mx;
            
                data[1][head] = input._aGTzid__my;
            
                data[2][head] = input._Tz3Q7P__mz;
            

            head++;
        }

        /**
         * Test if new chunk of data is available
         */
        bool isReady() {
            return head >= 76;
        }

    protected:
        uint32_t head;

        void shift() {
            // cap head
            if (head >= 76)
                head = 76;

            // shift data to the left by 19
            for (uint16_t ax = 0; ax < 3; ax++) {
                for (uint16_t i = 0; i < 57; i++)
                    data[ax][i] = data[ax][i + 19];
            }

            head = 76 - 19;
        }
};

    // ovr
    /**
 * Binary classification chain
 * Chain(blocks=[Window(length=1.0s, shift=0.25s, features=[Moments(), Autocorrelation(lag=1), Peaks(magnitude=0.1), CountAboveMean()]), Select(columns=['moments:min(my)', 'moments:std(my)', 'moments:max(mz)', 'moments:max(abs(mz))', 'moments:std(mz)', 'autocorrelation(mx)', 'autocorrelation(mz)', 'count_above_mean(mz)']), RandomForestClassifier(max_depth=7, min_samples_leaf=5, n_estimators=5)])
 */
 // feature extractors

/**
 * Moments()
 */
class _Ji4U62__moments_135010418199568_8438151137473 {
    public:

        void operator()(Window& window, Input& input) {
            
                // dimension: mx
                extract(window.data[0] + window.length - 76, &(input._XiOuCe__momentsminmx), &(input._kIX8Zh__momentsmaxmx), &(input._jSiICE__momentsmeanmx), &(input._IknBSj__momentsminabsmx), &(input._ypwfnt__momentsmaxabsmx), &(input._lnNby7__momentsmeanabsmx), &(input._vI9LHD__momentsstdmx) );
            
                // dimension: my
                extract(window.data[1] + window.length - 76, &(input._SalQct__momentsminmy), &(input._HRgdF2__momentsmaxmy), &(input._FkO1dy__momentsmeanmy), &(input._Oic8kL__momentsminabsmy), &(input._SxHu89__momentsmaxabsmy), &(input._x2BxiN__momentsmeanabsmy), &(input._F5bOdo__momentsstdmy) );
            
                // dimension: mz
                extract(window.data[2] + window.length - 76, &(input._082CHh__momentsminmz), &(input._EklLmr__momentsmaxmz), &(input._hqsjUF__momentsmeanmz), &(input._b2Fi2p__momentsminabsmz), &(input._clg7v2__momentsmaxabsmz), &(input._15tt2v__momentsmeanabsmz), &(input._Znwbtu__momentsstdmz) );
            
        }

    protected:

        void extract(float *array, float *minimum, float *maximum, float *average, float *absminimum, float *absmaximum, float *absaverage, float *stddev) {
            const float inverseCount = 0.013157894736842105f;
            float sum = 0;
            float absum = 0;
            float m = 3.402823466e+38F;
            float M = -3.402823466e+38F;
            float absm = 3.402823466e+38F;
            float absM = 0;

            // first pass (min, max, mean)
            for (uint16_t i = 0; i < 76; i++) {
                const float v = array[i];
                const float a = math::absolute(v);

                sum += v;
                absum += a;

                if (v < m) m = v;
                if (v > M) M = v;
                if (a < absm) absm = a;
                if (a > absM) absM = a;
            }

            const float mean = sum * inverseCount;
            float var = 0;
            float skew = 0;
            float kurtosis = 0;

            *minimum = m;
            *maximum = M;
            *average = mean;
            *absminimum = absm;
            *absmaximum = absM;
            *absaverage = absum * inverseCount;

            // second pass (std, skew, kurtosis)
            for (uint16_t i = 0; i < 76; i++) {
                const float v = array[i];
                const float d = v - mean;
                const float s = pow(d, 3);

                var += d * d;
                //skew += s;
                //kurtosis += s * d; // a.k.a. d^4
            }

            *stddev = std::sqrt(var * inverseCount);
            //*skew = sk / pow(var, 1.5) * inverseCount;
            //*kurtosis = kurt / pow(var, 2) * inverseCount;
        }
};

/**
 * Autocorrelation(lag=1)
 */
class _JhwKOl__autocorrelation_135010438076112_8438152379757 {
    public:

        void operator()(Window& window, Input& input) {
            
                // dimension: 
                extract(window.data[0] + window.length - 76, &(input._9XogdU__autocorrelationmx));
            
                // dimension: 
                extract(window.data[1] + window.length - 76, &(input._j861DZ__autocorrelationmy));
            
                // dimension: 
                extract(window.data[2] + window.length - 76, &(input._u0yBgY__autocorrelationmz));
            
        }

    protected:

        void extract(float *array, float *autocorrelation) {
            const float mean = np::mean(array, 76);
            float num = 0;
            float den = (array[0] - mean) * (array[0] - mean);

            // second pass (autocorrelation)
            for (uint16_t i = 1; i < 76; i++) {
                const float current = array[i - 1] - mean;
                const float next = array[i] - mean;

                num += current * next;
                den += next * next;
            }

            *autocorrelation = num / den;
        }
};

/**
 * Peaks(magnitude=0.1)
 */
class _pgCjr9__peaks_135010418209040_8438151138065 {
    public:

        void operator()(Window& window, Input& input) {
            
        }

    protected:

        void extract(float *array, float *peaksCount) {
            const float thres = (np::maximum(array, 76) - np::minimum(array, 76)) * 0.1f;
            uint16_t peaks = 0;

            for (uint16_t i = 1; i < 76 - 1; i++) {
                const float prev = array[i - 1];
                const float curr = array[i];
                const float next = array[i + 1];

                // check if peak
                if (math::absolute(curr - prev) > thres && math::absolute(curr - next) > thres)
                    peaks++;
            }

            *peaksCount = peaks / 74.0f;
        }
};

/**
 * CountAboveMean()
 */
class _7kapgA__countabovemean_135010418210704_8438151138169 {
    public:

        void operator()(Window& window, Input& input) {
            
                // dimension: 
                extract(window.data[0] + window.length - 76, &(input._zZmGqV__count_above_meanmx));
            
                // dimension: 
                extract(window.data[1] + window.length - 76, &(input._fz7hE5__count_above_meanmy));
            
                // dimension: 
                extract(window.data[2] + window.length - 76, &(input._V7ILZq__count_above_meanmz));
            
        }

    protected:

        void extract(float *array, float *countAboveMean) {
            const float mean = np::mean(array, 76);
            uint32_t count = 0;

            // second pass (count)
            for (uint16_t i = 0; i < 76; i++) {
                if (array[i] > mean)
                    count++;
            }

            *countAboveMean = count / 76f;
        }
};


// ovr block

class _CfCsro__select_135010443381648_8438152711353 {
    public:

        /**
         * Perform feature selection
         */
        void operator()(Input& input, Output& output) {
            // nothing to do, feature selection is only needed in Python
        }

        /**
         * Always ready
         */
        bool isReady() {
            return true;
        }
};

/**
 * DecisionTreeClassifier(max_depth=7, max_features='sqrt', min_samples_leaf=5,
                       random_state=634693766)
 */
class _UBTWUv__decisiontree_135010416219792_8438151013737 {
    public:

        void operator()(Input& input, Output& output) {
            
                
    if (input._EklLmr__momentsmaxmz < 0.4417639374732971f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.8995633187772926;
    return;

    }
    else {
        
    if (input._V7ILZq__count_above_meanmz < 0.4802631586790085f) {
        
    if (input._Znwbtu__momentsstdmz < 0.10946521162986755f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.8995633187772926;
    return;

    }
    else {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.8995633187772926;
    return;

    }

    }
    else {
        
    if (input._clg7v2__momentsmaxabsmz < 0.4511711299419403f) {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.10043668122270742;
    return;

    }
    else {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.8995633187772926;
    return;

    }

    }

    }

            
        }

        bool isReady() {
            return true;
        }
};/**
 * DecisionTreeClassifier(max_depth=7, max_features='sqrt', min_samples_leaf=5,
                       random_state=1462636145)
 */
class _ntqsHu__decisiontree_135010416216592_8438151013537 {
    public:

        void operator()(Input& input, Output& output) {
            
                
    if (input._9XogdU__autocorrelationmx < 0.9719353020191193f) {
        
    if (input._9XogdU__autocorrelationmx < 0.9492263197898865f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9039301310043668;
    return;

    }
    else {
        
    if (input._V7ILZq__count_above_meanmz < 0.6052631437778473f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9039301310043668;
    return;

    }
    else {
        
    if (input._u0yBgY__autocorrelationmz < 0.9477763772010803f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9039301310043668;
    return;

    }
    else {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.09606986899563319;
    return;

    }

    }

    }

    }
    else {
        
    if (input._EklLmr__momentsmaxmz < 0.42119477689266205f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9039301310043668;
    return;

    }
    else {
        
    if (input._SalQct__momentsminmy < 0.49766869843006134f) {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.09606986899563319;
    return;

    }
    else {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.09606986899563319;
    return;

    }

    }

    }

            
        }

        bool isReady() {
            return true;
        }
};/**
 * DecisionTreeClassifier(max_depth=7, max_features='sqrt', min_samples_leaf=5,
                       random_state=779719661)
 */
class _GpsrFl__decisiontree_135010414289616_8438150893101 {
    public:

        void operator()(Input& input, Output& output) {
            
                
    if (input._9XogdU__autocorrelationmx < 0.9719353020191193f) {
        
    if (input._clg7v2__momentsmaxabsmz < 0.44988173246383667f) {
        
    if (input._9XogdU__autocorrelationmx < 0.9608582556247711f) {
        
    if (input._SalQct__momentsminmy < 0.490614578127861f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.8864628820960698;
    return;

    }
    else {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.8864628820960698;
    return;

    }

    }
    else {
        
    if (input._V7ILZq__count_above_meanmz < 0.5986841917037964f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.8864628820960698;
    return;

    }
    else {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.11353711790393013;
    return;

    }

    }

    }
    else {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.8864628820960698;
    return;

    }

    }
    else {
        
    if (input._clg7v2__momentsmaxabsmz < 0.42119477689266205f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.8864628820960698;
    return;

    }
    else {
        
    if (input._F5bOdo__momentsstdmy < 0.040333088487386703f) {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.11353711790393013;
    return;

    }
    else {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.11353711790393013;
    return;

    }

    }

    }

            
        }

        bool isReady() {
            return true;
        }
};/**
 * DecisionTreeClassifier(max_depth=7, max_features='sqrt', min_samples_leaf=5,
                       random_state=564417876)
 */
class _EFbUe3__decisiontree_135010416099984_8438151006249 {
    public:

        void operator()(Input& input, Output& output) {
            
                
    if (input._F5bOdo__momentsstdmy < 0.026905834674835205f) {
        
    if (input._Znwbtu__momentsstdmz < 0.08127773925662041f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9082969432314411;
    return;

    }
    else {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9082969432314411;
    return;

    }

    }
    else {
        
    if (input._EklLmr__momentsmaxmz < 0.451583132147789f) {
        
    if (input._u0yBgY__autocorrelationmz < 0.9694318473339081f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9082969432314411;
    return;

    }
    else {
        
    if (input._EklLmr__momentsmaxmz < 0.4453650712966919f) {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.09170305676855896;
    return;

    }
    else {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.09170305676855896;
    return;

    }

    }

    }
    else {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9082969432314411;
    return;

    }

    }

            
        }

        bool isReady() {
            return true;
        }
};/**
 * DecisionTreeClassifier(max_depth=7, max_features='sqrt', min_samples_leaf=5,
                       random_state=1997449201)
 */
class _XPvgug__decisiontree_135010413490896_8438150843181 {
    public:

        void operator()(Input& input, Output& output) {
            
                
    if (input._u0yBgY__autocorrelationmz < 0.9801578521728516f) {
        
    if (input._9XogdU__autocorrelationmx < 0.9608582556247711f) {
        
    if (input._Znwbtu__momentsstdmz < 0.10383052006363869f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.925764192139738;
    return;

    }
    else {
        
    if (input._9XogdU__autocorrelationmx < 0.9468507170677185f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.925764192139738;
    return;

    }
    else {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.925764192139738;
    return;

    }

    }

    }
    else {
        
    if (input._clg7v2__momentsmaxabsmz < 0.42119477689266205f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.925764192139738;
    return;

    }
    else {
        
    if (input._Znwbtu__momentsstdmz < 0.16490818560123444f) {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.07423580786026202;
    return;

    }
    else {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.925764192139738;
    return;

    }

    }

    }

    }
    else {
        
    if (input._clg7v2__momentsmaxabsmz < 0.42119477689266205f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.925764192139738;
    return;

    }
    else {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.07423580786026202;
    return;

    }

    }

            
        }

        bool isReady() {
            return true;
        }
};

class _4XyMOZ__randomforest_135010438375248_8438152398453 {
    public:
        void operator()(Input& input, Output& output) {
            Output treeOutput;
            float scores[2] = { 0 };

            // iterate over trees
            
                tree1(input, treeOutput);
                scores[treeOutput.classification.idx] += 1;
            
                tree2(input, treeOutput);
                scores[treeOutput.classification.idx] += 1;
            
                tree3(input, treeOutput);
                scores[treeOutput.classification.idx] += 1;
            
                tree4(input, treeOutput);
                scores[treeOutput.classification.idx] += 1;
            
                tree5(input, treeOutput);
                scores[treeOutput.classification.idx] += 1;
            

            // get output with highest vote
            output.classification.idx = 0;
            output.classification.confidence = scores[0];

            for (uint8_t i = 1; i < 2; i++) {
                if (scores[i] > output.classification.confidence) {
                    output.classification.idx = i;
                    output.classification.confidence = scores[i];
                }
            }
        }

        /**
         * Always ready
         */
        bool isReady() {
            return true;
        }

    protected:
        
            _UBTWUv__decisiontree_135010416219792_8438151013737 tree1;
        
            _ntqsHu__decisiontree_135010416216592_8438151013537 tree2;
        
            _GpsrFl__decisiontree_135010414289616_8438150893101 tree3;
        
            _EFbUe3__decisiontree_135010416099984_8438151006249 tree4;
        
            _XPvgug__decisiontree_135010413490896_8438150843181 tree5;
        
};


// chain
class _9wtN79__binarychain_135010442705232_8438152669077 {
    public:

    _9wtN79__binarychain_135010442705232_8438152669077() : ready(false) {

    }

    void operator()(Window& window, Input& input, Output& output) {
        extractFeatures(window, input);

        // ovr
        
            block1(input, output);

            if (!block1.isReady()) {
                ready = false;
                return;
            }
        
            block2(input, output);

            if (!block2.isReady()) {
                ready = false;
                return;
            }
        

        ready = true;
    }

    bool isReady() {
        return ready;
    }

    protected:
        bool ready;

        
            _Ji4U62__moments_135010418199568_8438151137473 extr1;
        
            _JhwKOl__autocorrelation_135010438076112_8438152379757 extr2;
        
            _pgCjr9__peaks_135010418209040_8438151138065 extr3;
        
            _7kapgA__countabovemean_135010418210704_8438151138169 extr4;
        

        
            // Select(columns=['moments:min(my)', 'moments:std(my)', 'moments:max(mz)', 'moments:max(abs(mz))', 'moments:std(mz)', 'autocorrelation(mx)', 'autocorrelation(mz)', 'count_above_mean(mz)'])
            _CfCsro__select_135010443381648_8438152711353 block1;
        
            // RandomForestClassifier(max_depth=7, min_samples_leaf=5, n_estimators=5)
            _4XyMOZ__randomforest_135010438375248_8438152398453 block2;
        

        void extractFeatures(Window& window, Input& input) {
            
                extr1(window, input);
            
                extr2(window, input);
            
                extr3(window, input);
            
                extr4(window, input);
            
        }

};/**
 * Binary classification chain
 * Chain(blocks=[Window(length=1.0s, shift=0.25s, features=[Moments(), Autocorrelation(lag=1), Peaks(magnitude=0.1), CountAboveMean()]), Select(columns=['moments:min(mz)', 'moments:max(mz)', 'moments:max(abs(mz))', 'autocorrelation(mz)', 'peaks(my)', 'peaks(mz)', 'count_above_mean(mx)', 'count_above_mean(mz)']), RandomForestClassifier(max_depth=7, min_samples_leaf=5, n_estimators=5)])
 */
 // feature extractors

/**
 * Moments()
 */
class _xPNBRW__moments_135010413492432_8438150843277 {
    public:

        void operator()(Window& window, Input& input) {
            
                // dimension: mx
                extract(window.data[0] + window.length - 76, &(input._XiOuCe__momentsminmx), &(input._kIX8Zh__momentsmaxmx), &(input._jSiICE__momentsmeanmx), &(input._IknBSj__momentsminabsmx), &(input._ypwfnt__momentsmaxabsmx), &(input._lnNby7__momentsmeanabsmx), &(input._vI9LHD__momentsstdmx) );
            
                // dimension: my
                extract(window.data[1] + window.length - 76, &(input._SalQct__momentsminmy), &(input._HRgdF2__momentsmaxmy), &(input._FkO1dy__momentsmeanmy), &(input._Oic8kL__momentsminabsmy), &(input._SxHu89__momentsmaxabsmy), &(input._x2BxiN__momentsmeanabsmy), &(input._F5bOdo__momentsstdmy) );
            
                // dimension: mz
                extract(window.data[2] + window.length - 76, &(input._082CHh__momentsminmz), &(input._EklLmr__momentsmaxmz), &(input._hqsjUF__momentsmeanmz), &(input._b2Fi2p__momentsminabsmz), &(input._clg7v2__momentsmaxabsmz), &(input._15tt2v__momentsmeanabsmz), &(input._Znwbtu__momentsstdmz) );
            
        }

    protected:

        void extract(float *array, float *minimum, float *maximum, float *average, float *absminimum, float *absmaximum, float *absaverage, float *stddev) {
            const float inverseCount = 0.013157894736842105f;
            float sum = 0;
            float absum = 0;
            float m = 3.402823466e+38F;
            float M = -3.402823466e+38F;
            float absm = 3.402823466e+38F;
            float absM = 0;

            // first pass (min, max, mean)
            for (uint16_t i = 0; i < 76; i++) {
                const float v = array[i];
                const float a = math::absolute(v);

                sum += v;
                absum += a;

                if (v < m) m = v;
                if (v > M) M = v;
                if (a < absm) absm = a;
                if (a > absM) absM = a;
            }

            const float mean = sum * inverseCount;
            float var = 0;
            float skew = 0;
            float kurtosis = 0;

            *minimum = m;
            *maximum = M;
            *average = mean;
            *absminimum = absm;
            *absmaximum = absM;
            *absaverage = absum * inverseCount;

            // second pass (std, skew, kurtosis)
            for (uint16_t i = 0; i < 76; i++) {
                const float v = array[i];
                const float d = v - mean;
                const float s = pow(d, 3);

                var += d * d;
                //skew += s;
                //kurtosis += s * d; // a.k.a. d^4
            }

            *stddev = std::sqrt(var * inverseCount);
            //*skew = sk / pow(var, 1.5) * inverseCount;
            //*kurtosis = kurt / pow(var, 2) * inverseCount;
        }
};

/**
 * Autocorrelation(lag=1)
 */
class _2IKYmw__autocorrelation_135010413492496_8438150843281 {
    public:

        void operator()(Window& window, Input& input) {
            
                // dimension: 
                extract(window.data[0] + window.length - 76, &(input._9XogdU__autocorrelationmx));
            
                // dimension: 
                extract(window.data[1] + window.length - 76, &(input._j861DZ__autocorrelationmy));
            
                // dimension: 
                extract(window.data[2] + window.length - 76, &(input._u0yBgY__autocorrelationmz));
            
        }

    protected:

        void extract(float *array, float *autocorrelation) {
            const float mean = np::mean(array, 76);
            float num = 0;
            float den = (array[0] - mean) * (array[0] - mean);

            // second pass (autocorrelation)
            for (uint16_t i = 1; i < 76; i++) {
                const float current = array[i - 1] - mean;
                const float next = array[i] - mean;

                num += current * next;
                den += next * next;
            }

            *autocorrelation = num / den;
        }
};

/**
 * Peaks(magnitude=0.1)
 */
class _IZvC2V__peaks_135010413492560_8438150843285 {
    public:

        void operator()(Window& window, Input& input) {
            
        }

    protected:

        void extract(float *array, float *peaksCount) {
            const float thres = (np::maximum(array, 76) - np::minimum(array, 76)) * 0.1f;
            uint16_t peaks = 0;

            for (uint16_t i = 1; i < 76 - 1; i++) {
                const float prev = array[i - 1];
                const float curr = array[i];
                const float next = array[i + 1];

                // check if peak
                if (math::absolute(curr - prev) > thres && math::absolute(curr - next) > thres)
                    peaks++;
            }

            *peaksCount = peaks / 74.0f;
        }
};

/**
 * CountAboveMean()
 */
class _gys7px__countabovemean_135010421283664_8438151330229 {
    public:

        void operator()(Window& window, Input& input) {
            
                // dimension: 
                extract(window.data[0] + window.length - 76, &(input._zZmGqV__count_above_meanmx));
            
                // dimension: 
                extract(window.data[1] + window.length - 76, &(input._fz7hE5__count_above_meanmy));
            
                // dimension: 
                extract(window.data[2] + window.length - 76, &(input._V7ILZq__count_above_meanmz));
            
        }

    protected:

        void extract(float *array, float *countAboveMean) {
            const float mean = np::mean(array, 76);
            uint32_t count = 0;

            // second pass (count)
            for (uint16_t i = 0; i < 76; i++) {
                if (array[i] > mean)
                    count++;
            }

            *countAboveMean = count / 76f;
        }
};


// ovr block

class _z0JlpP__select_135010415255888_8438150953493 {
    public:

        /**
         * Perform feature selection
         */
        void operator()(Input& input, Output& output) {
            // nothing to do, feature selection is only needed in Python
        }

        /**
         * Always ready
         */
        bool isReady() {
            return true;
        }
};

/**
 * DecisionTreeClassifier(max_depth=7, max_features='sqrt', min_samples_leaf=5,
                       random_state=460618015)
 */
class _oDsKD6__decisiontree_135010426027792_8438151626737 {
    public:

        void operator()(Input& input, Output& output) {
            
                
    if (input._082CHh__momentsminmz < 0.04469367489218712f) {
        
    if (input._EklLmr__momentsmaxmz < 0.9950713217258453f) {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.08333333333333333;
    return;

    }
    else {
        
    if (input._zZmGqV__count_above_meanmx < 0.664473682641983f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9166666666666666;
    return;

    }
    else {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9166666666666666;
    return;

    }

    }

    }
    else {
        
    if (input._zZmGqV__count_above_meanmx < 0.5197368562221527f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9166666666666666;
    return;

    }
    else {
        
    if (input._EklLmr__momentsmaxmz < 0.5357366353273392f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9166666666666666;
    return;

    }
    else {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9166666666666666;
    return;

    }

    }

    }

            
        }

        bool isReady() {
            return true;
        }
};/**
 * DecisionTreeClassifier(max_depth=7, max_features='sqrt', min_samples_leaf=5,
                       random_state=1057889463)
 */
class _dMGveq__decisiontree_135010414294352_8438150893397 {
    public:

        void operator()(Input& input, Output& output) {
            
                
    if (input._EklLmr__momentsmaxmz < 0.5161898285150528f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9458333333333333;
    return;

    }
    else {
        
    if (input._EklLmr__momentsmaxmz < 0.9950713217258453f) {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.05416666666666667;
    return;

    }
    else {
        
    if (input._u0yBgY__autocorrelationmz < 0.9199385344982147f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9458333333333333;
    return;

    }
    else {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9458333333333333;
    return;

    }

    }

    }

            
        }

        bool isReady() {
            return true;
        }
};/**
 * DecisionTreeClassifier(max_depth=7, max_features='sqrt', min_samples_leaf=5,
                       random_state=511667211)
 */
class _cAr0Lk__decisiontree_135010416309712_8438151019357 {
    public:

        void operator()(Input& input, Output& output) {
            
                
    if (input._clg7v2__momentsmaxabsmz < 0.5658350437879562f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9166666666666666;
    return;

    }
    else {
        
    if (input._km4spH__peaksmz < 0.0810810811817646f) {
        
    if (input._u0yBgY__autocorrelationmz < 0.9256716966629028f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9166666666666666;
    return;

    }
    else {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9166666666666666;
    return;

    }

    }
    else {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.08333333333333333;
    return;

    }

    }

            
        }

        bool isReady() {
            return true;
        }
};/**
 * DecisionTreeClassifier(max_depth=7, max_features='sqrt', min_samples_leaf=5,
                       random_state=1129702123)
 */
class _jXy5kf__decisiontree_135010416310928_8438151019433 {
    public:

        void operator()(Input& input, Output& output) {
            
                
    if (input._clg7v2__momentsmaxabsmz < 0.5161898285150528f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9375;
    return;

    }
    else {
        
    if (input._zZmGqV__count_above_meanmx < 0.5723684430122375f) {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.0625;
    return;

    }
    else {
        
    if (input._u0yBgY__autocorrelationmz < 0.9199385344982147f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9375;
    return;

    }
    else {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9375;
    return;

    }

    }

    }

            
        }

        bool isReady() {
            return true;
        }
};/**
 * DecisionTreeClassifier(max_depth=7, max_features='sqrt', min_samples_leaf=5,
                       random_state=1158479728)
 */
class _o8beqq__decisiontree_135010413509456_8438150844341 {
    public:

        void operator()(Input& input, Output& output) {
            
                
    if (input._u0yBgY__autocorrelationmz < 0.949573278427124f) {
        
    if (input._082CHh__momentsminmz < 0.2667277157306671f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.8791666666666667;
    return;

    }
    else {
        
    if (input._zZmGqV__count_above_meanmx < 0.5328947603702545f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.8791666666666667;
    return;

    }
    else {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.8791666666666667;
    return;

    }

    }

    }
    else {
        
    if (input._u0yBgY__autocorrelationmz < 0.9730337262153625f) {
        
    if (input._km4spH__peaksmz < 0.06081080995500088f) {
        
    if (input._zZmGqV__count_above_meanmx < 0.625f) {
        
    if (input._ZP45RY__peaksmy < 0.06756756640970707f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.8791666666666667;
    return;

    }
    else {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.8791666666666667;
    return;

    }

    }
    else {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.8791666666666667;
    return;

    }

    }
    else {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.12083333333333333;
    return;

    }

    }
    else {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.8791666666666667;
    return;

    }

    }

            
        }

        bool isReady() {
            return true;
        }
};

class _UT99wQ__randomforest_135010438371408_8438152398213 {
    public:
        void operator()(Input& input, Output& output) {
            Output treeOutput;
            float scores[2] = { 0 };

            // iterate over trees
            
                tree1(input, treeOutput);
                scores[treeOutput.classification.idx] += 1;
            
                tree2(input, treeOutput);
                scores[treeOutput.classification.idx] += 1;
            
                tree3(input, treeOutput);
                scores[treeOutput.classification.idx] += 1;
            
                tree4(input, treeOutput);
                scores[treeOutput.classification.idx] += 1;
            
                tree5(input, treeOutput);
                scores[treeOutput.classification.idx] += 1;
            

            // get output with highest vote
            output.classification.idx = 0;
            output.classification.confidence = scores[0];

            for (uint8_t i = 1; i < 2; i++) {
                if (scores[i] > output.classification.confidence) {
                    output.classification.idx = i;
                    output.classification.confidence = scores[i];
                }
            }
        }

        /**
         * Always ready
         */
        bool isReady() {
            return true;
        }

    protected:
        
            _oDsKD6__decisiontree_135010426027792_8438151626737 tree1;
        
            _dMGveq__decisiontree_135010414294352_8438150893397 tree2;
        
            _cAr0Lk__decisiontree_135010416309712_8438151019357 tree3;
        
            _jXy5kf__decisiontree_135010416310928_8438151019433 tree4;
        
            _o8beqq__decisiontree_135010413509456_8438150844341 tree5;
        
};


// chain
class _ZNFaTj__binarychain_135010413492112_8438150843257 {
    public:

    _ZNFaTj__binarychain_135010413492112_8438150843257() : ready(false) {

    }

    void operator()(Window& window, Input& input, Output& output) {
        extractFeatures(window, input);

        // ovr
        
            block1(input, output);

            if (!block1.isReady()) {
                ready = false;
                return;
            }
        
            block2(input, output);

            if (!block2.isReady()) {
                ready = false;
                return;
            }
        

        ready = true;
    }

    bool isReady() {
        return ready;
    }

    protected:
        bool ready;

        
            _xPNBRW__moments_135010413492432_8438150843277 extr1;
        
            _2IKYmw__autocorrelation_135010413492496_8438150843281 extr2;
        
            _IZvC2V__peaks_135010413492560_8438150843285 extr3;
        
            _gys7px__countabovemean_135010421283664_8438151330229 extr4;
        

        
            // Select(columns=['moments:min(mz)', 'moments:max(mz)', 'moments:max(abs(mz))', 'autocorrelation(mz)', 'peaks(my)', 'peaks(mz)', 'count_above_mean(mx)', 'count_above_mean(mz)'])
            _z0JlpP__select_135010415255888_8438150953493 block1;
        
            // RandomForestClassifier(max_depth=7, min_samples_leaf=5, n_estimators=5)
            _UT99wQ__randomforest_135010438371408_8438152398213 block2;
        

        void extractFeatures(Window& window, Input& input) {
            
                extr1(window, input);
            
                extr2(window, input);
            
                extr3(window, input);
            
                extr4(window, input);
            
        }

};/**
 * Binary classification chain
 * Chain(blocks=[Window(length=1.0s, shift=0.25s, features=[Moments(), Autocorrelation(lag=1), Peaks(magnitude=0.1), CountAboveMean()]), Select(columns=['moments:std(my)', 'moments:max(mz)', 'moments:mean(mz)', 'moments:max(abs(mz))', 'moments:mean(abs(mz))', 'count_above_mean(mx)', 'count_above_mean(my)', 'count_above_mean(mz)']), RandomForestClassifier(max_depth=7, min_samples_leaf=5, n_estimators=5)])
 */
 // feature extractors

/**
 * Moments()
 */
class _uSGeRc__moments_135010430201872_8438151887617 {
    public:

        void operator()(Window& window, Input& input) {
            
                // dimension: mx
                extract(window.data[0] + window.length - 76, &(input._XiOuCe__momentsminmx), &(input._kIX8Zh__momentsmaxmx), &(input._jSiICE__momentsmeanmx), &(input._IknBSj__momentsminabsmx), &(input._ypwfnt__momentsmaxabsmx), &(input._lnNby7__momentsmeanabsmx), &(input._vI9LHD__momentsstdmx) );
            
                // dimension: my
                extract(window.data[1] + window.length - 76, &(input._SalQct__momentsminmy), &(input._HRgdF2__momentsmaxmy), &(input._FkO1dy__momentsmeanmy), &(input._Oic8kL__momentsminabsmy), &(input._SxHu89__momentsmaxabsmy), &(input._x2BxiN__momentsmeanabsmy), &(input._F5bOdo__momentsstdmy) );
            
                // dimension: mz
                extract(window.data[2] + window.length - 76, &(input._082CHh__momentsminmz), &(input._EklLmr__momentsmaxmz), &(input._hqsjUF__momentsmeanmz), &(input._b2Fi2p__momentsminabsmz), &(input._clg7v2__momentsmaxabsmz), &(input._15tt2v__momentsmeanabsmz), &(input._Znwbtu__momentsstdmz) );
            
        }

    protected:

        void extract(float *array, float *minimum, float *maximum, float *average, float *absminimum, float *absmaximum, float *absaverage, float *stddev) {
            const float inverseCount = 0.013157894736842105f;
            float sum = 0;
            float absum = 0;
            float m = 3.402823466e+38F;
            float M = -3.402823466e+38F;
            float absm = 3.402823466e+38F;
            float absM = 0;

            // first pass (min, max, mean)
            for (uint16_t i = 0; i < 76; i++) {
                const float v = array[i];
                const float a = math::absolute(v);

                sum += v;
                absum += a;

                if (v < m) m = v;
                if (v > M) M = v;
                if (a < absm) absm = a;
                if (a > absM) absM = a;
            }

            const float mean = sum * inverseCount;
            float var = 0;
            float skew = 0;
            float kurtosis = 0;

            *minimum = m;
            *maximum = M;
            *average = mean;
            *absminimum = absm;
            *absmaximum = absM;
            *absaverage = absum * inverseCount;

            // second pass (std, skew, kurtosis)
            for (uint16_t i = 0; i < 76; i++) {
                const float v = array[i];
                const float d = v - mean;
                const float s = pow(d, 3);

                var += d * d;
                //skew += s;
                //kurtosis += s * d; // a.k.a. d^4
            }

            *stddev = std::sqrt(var * inverseCount);
            //*skew = sk / pow(var, 1.5) * inverseCount;
            //*kurtosis = kurt / pow(var, 2) * inverseCount;
        }
};

/**
 * Autocorrelation(lag=1)
 */
class _U0YfRr__autocorrelation_135010425454032_8438151590877 {
    public:

        void operator()(Window& window, Input& input) {
            
                // dimension: 
                extract(window.data[0] + window.length - 76, &(input._9XogdU__autocorrelationmx));
            
                // dimension: 
                extract(window.data[1] + window.length - 76, &(input._j861DZ__autocorrelationmy));
            
                // dimension: 
                extract(window.data[2] + window.length - 76, &(input._u0yBgY__autocorrelationmz));
            
        }

    protected:

        void extract(float *array, float *autocorrelation) {
            const float mean = np::mean(array, 76);
            float num = 0;
            float den = (array[0] - mean) * (array[0] - mean);

            // second pass (autocorrelation)
            for (uint16_t i = 1; i < 76; i++) {
                const float current = array[i - 1] - mean;
                const float next = array[i] - mean;

                num += current * next;
                den += next * next;
            }

            *autocorrelation = num / den;
        }
};

/**
 * Peaks(magnitude=0.1)
 */
class _WNpsxz__peaks_135010440328784_8438152520549 {
    public:

        void operator()(Window& window, Input& input) {
            
        }

    protected:

        void extract(float *array, float *peaksCount) {
            const float thres = (np::maximum(array, 76) - np::minimum(array, 76)) * 0.1f;
            uint16_t peaks = 0;

            for (uint16_t i = 1; i < 76 - 1; i++) {
                const float prev = array[i - 1];
                const float curr = array[i];
                const float next = array[i + 1];

                // check if peak
                if (math::absolute(curr - prev) > thres && math::absolute(curr - next) > thres)
                    peaks++;
            }

            *peaksCount = peaks / 74.0f;
        }
};

/**
 * CountAboveMean()
 */
class _EYdbAH__countabovemean_135010440322384_8438152520149 {
    public:

        void operator()(Window& window, Input& input) {
            
                // dimension: 
                extract(window.data[0] + window.length - 76, &(input._zZmGqV__count_above_meanmx));
            
                // dimension: 
                extract(window.data[1] + window.length - 76, &(input._fz7hE5__count_above_meanmy));
            
                // dimension: 
                extract(window.data[2] + window.length - 76, &(input._V7ILZq__count_above_meanmz));
            
        }

    protected:

        void extract(float *array, float *countAboveMean) {
            const float mean = np::mean(array, 76);
            uint32_t count = 0;

            // second pass (count)
            for (uint16_t i = 0; i < 76; i++) {
                if (array[i] > mean)
                    count++;
            }

            *countAboveMean = count / 76f;
        }
};


// ovr block

class _Pv64ax__select_135010440184272_8438152511517 {
    public:

        /**
         * Perform feature selection
         */
        void operator()(Input& input, Output& output) {
            // nothing to do, feature selection is only needed in Python
        }

        /**
         * Always ready
         */
        bool isReady() {
            return true;
        }
};

/**
 * DecisionTreeClassifier(max_depth=7, max_features='sqrt', min_samples_leaf=5,
                       random_state=1478507652)
 */
class _aJHydV__decisiontree_135010413495888_8438150843493 {
    public:

        void operator()(Input& input, Output& output) {
            
                
    if (input._clg7v2__momentsmaxabsmz < 0.9950713217258453f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.8951965065502183;
    return;

    }
    else {
        
    if (input._fz7hE5__count_above_meanmy < 0.5065789371728897f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.8951965065502183;
    return;

    }
    else {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.10480349344978165;
    return;

    }

    }

            
        }

        bool isReady() {
            return true;
        }
};/**
 * DecisionTreeClassifier(max_depth=7, max_features='sqrt', min_samples_leaf=5,
                       random_state=1109837477)
 */
class _roWB5q__decisiontree_135010417346000_8438151084125 {
    public:

        void operator()(Input& input, Output& output) {
            
                
    if (input._clg7v2__momentsmaxabsmz < 0.9950713217258453f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.8908296943231441;
    return;

    }
    else {
        
    if (input._hqsjUF__momentsmeanmz < 0.42816945910453796f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.8908296943231441;
    return;

    }
    else {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.1091703056768559;
    return;

    }

    }

            
        }

        bool isReady() {
            return true;
        }
};/**
 * DecisionTreeClassifier(max_depth=7, max_features='sqrt', min_samples_leaf=5,
                       random_state=1926453635)
 */
class _OqSEAC__decisiontree_135010414375696_8438150898481 {
    public:

        void operator()(Input& input, Output& output) {
            
                
    if (input._clg7v2__momentsmaxabsmz < 0.9950713217258453f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.8995633187772926;
    return;

    }
    else {
        
    if (input._hqsjUF__momentsmeanmz < 0.42823822796344757f) {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.10043668122270742;
    return;

    }
    else {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.10043668122270742;
    return;

    }

    }

            
        }

        bool isReady() {
            return true;
        }
};/**
 * DecisionTreeClassifier(max_depth=7, max_features='sqrt', min_samples_leaf=5,
                       random_state=1894213183)
 */
class _jD4YN8__decisiontree_135010415252368_8438150953273 {
    public:

        void operator()(Input& input, Output& output) {
            
                
    if (input._F5bOdo__momentsstdmy < 0.15865562111139297f) {
        
    if (input._V7ILZq__count_above_meanmz < 0.14473684132099152f) {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.11353711790393013;
    return;

    }
    else {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.8864628820960698;
    return;

    }

    }
    else {
        
    if (input._V7ILZq__count_above_meanmz < 0.28947368264198303f) {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.11353711790393013;
    return;

    }
    else {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.8864628820960698;
    return;

    }

    }

            
        }

        bool isReady() {
            return true;
        }
};/**
 * DecisionTreeClassifier(max_depth=7, max_features='sqrt', min_samples_leaf=5,
                       random_state=1086979636)
 */
class _6foHU3__decisiontree_135010415263440_8438150953965 {
    public:

        void operator()(Input& input, Output& output) {
            
                
    if (input._hqsjUF__momentsmeanmz < 0.42652399837970734f) {
        
    if (input._F5bOdo__momentsstdmy < 0.1455494910478592f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9388646288209607;
    return;

    }
    else {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9388646288209607;
    return;

    }

    }
    else {
        
    if (input._EklLmr__momentsmaxmz < 0.9950713217258453f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9388646288209607;
    return;

    }
    else {
        
    if (input._hqsjUF__momentsmeanmz < 0.44203880429267883f) {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.0611353711790393;
    return;

    }
    else {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.0611353711790393;
    return;

    }

    }

    }

            
        }

        bool isReady() {
            return true;
        }
};

class _8hbXRw__randomforest_135010429437712_8438151839857 {
    public:
        void operator()(Input& input, Output& output) {
            Output treeOutput;
            float scores[2] = { 0 };

            // iterate over trees
            
                tree1(input, treeOutput);
                scores[treeOutput.classification.idx] += 1;
            
                tree2(input, treeOutput);
                scores[treeOutput.classification.idx] += 1;
            
                tree3(input, treeOutput);
                scores[treeOutput.classification.idx] += 1;
            
                tree4(input, treeOutput);
                scores[treeOutput.classification.idx] += 1;
            
                tree5(input, treeOutput);
                scores[treeOutput.classification.idx] += 1;
            

            // get output with highest vote
            output.classification.idx = 0;
            output.classification.confidence = scores[0];

            for (uint8_t i = 1; i < 2; i++) {
                if (scores[i] > output.classification.confidence) {
                    output.classification.idx = i;
                    output.classification.confidence = scores[i];
                }
            }
        }

        /**
         * Always ready
         */
        bool isReady() {
            return true;
        }

    protected:
        
            _aJHydV__decisiontree_135010413495888_8438150843493 tree1;
        
            _roWB5q__decisiontree_135010417346000_8438151084125 tree2;
        
            _OqSEAC__decisiontree_135010414375696_8438150898481 tree3;
        
            _jD4YN8__decisiontree_135010415252368_8438150953273 tree4;
        
            _6foHU3__decisiontree_135010415263440_8438150953965 tree5;
        
};


// chain
class _3cnwH0__binarychain_135010440334096_8438152520881 {
    public:

    _3cnwH0__binarychain_135010440334096_8438152520881() : ready(false) {

    }

    void operator()(Window& window, Input& input, Output& output) {
        extractFeatures(window, input);

        // ovr
        
            block1(input, output);

            if (!block1.isReady()) {
                ready = false;
                return;
            }
        
            block2(input, output);

            if (!block2.isReady()) {
                ready = false;
                return;
            }
        

        ready = true;
    }

    bool isReady() {
        return ready;
    }

    protected:
        bool ready;

        
            _uSGeRc__moments_135010430201872_8438151887617 extr1;
        
            _U0YfRr__autocorrelation_135010425454032_8438151590877 extr2;
        
            _WNpsxz__peaks_135010440328784_8438152520549 extr3;
        
            _EYdbAH__countabovemean_135010440322384_8438152520149 extr4;
        

        
            // Select(columns=['moments:std(my)', 'moments:max(mz)', 'moments:mean(mz)', 'moments:max(abs(mz))', 'moments:mean(abs(mz))', 'count_above_mean(mx)', 'count_above_mean(my)', 'count_above_mean(mz)'])
            _Pv64ax__select_135010440184272_8438152511517 block1;
        
            // RandomForestClassifier(max_depth=7, min_samples_leaf=5, n_estimators=5)
            _8hbXRw__randomforest_135010429437712_8438151839857 block2;
        

        void extractFeatures(Window& window, Input& input) {
            
                extr1(window, input);
            
                extr2(window, input);
            
                extr3(window, input);
            
                extr4(window, input);
            
        }

};

    /**
     * Chain class
     * Chain(blocks=[])
     */
     class MediaControlChain {
        public:
            Input input;
            Output output;
            String label;
            Input inputs[3];
            Output outputs[3];
            Classmap classmap;

            /**
 * Transform Input
 */
bool operator()(const Input& input) {
    return operator()(input._PSawsX__mx, input._aGTzid__my, input._Tz3Q7P__mz);
}

/**
 * Transform array input
 */
bool operator()(float *inputs) {
    return operator()(inputs[0], inputs[1], inputs[2]);
}

/**
 * Transform const array input
 */
bool operator()(const float *inputs) {
    return operator()(inputs[0], inputs[1], inputs[2]);
}


            /**
             * Transform input
             */
            bool operator()(const float _PSawsX__mx, const float _aGTzid__my, const float _Tz3Q7P__mz) {
                // assign variables to input
                
                    input._PSawsX__mx = _PSawsX__mx;
                
                    input._aGTzid__my = _aGTzid__my;
                
                    input._Tz3Q7P__mz = _Tz3Q7P__mz;
                

                
                    // run pre-processing blocks
                    if (!pre(input._PSawsX__mx, input._aGTzid__my, input._Tz3Q7P__mz))
                        return false;

                    // copy pre.input to input
                    
                        input._PSawsX__mx = pre.input._PSawsX__mx;
                    
                        input._aGTzid__my = pre.input._aGTzid__my;
                    
                        input._Tz3Q7P__mz = pre.input._Tz3Q7P__mz;
                    
                


                // windowing
                window(input);

                if (!window.isReady())
                    return false;

                // feature extraction + ovr for each binary classification chain
                
                    inputs[0].copyFrom(input);
                    chain1(window, inputs[0], outputs[0]);
                
                    inputs[1].copyFrom(input);
                    chain2(window, inputs[1], outputs[1]);
                
                    inputs[2].copyFrom(input);
                    chain3(window, inputs[2], outputs[2]);
                

                // get positive classification with highest confidence
                int8_t idx = -1;
                float confidence = 0;

                for (uint8_t i = 0; i < 3; i++) {
                    if (outputs[i].classification.idx > 0 && outputs[i].classification.confidence > confidence) {
                        idx = i;
                        confidence = outputs[i].classification.confidence;
                    }
                }

                output.classification.prevIdx = output.classification.idx;
                output.classification.prevConfidence = output.classification.confidence;
                output.classification.idx = idx;
                output.classification.confidence = confidence;
                output.classification.label = classmap.get(idx);
                label = output.classification.label;

                return true;
            }

        protected:
            
            internals::tinyml4all::PreprocessingChain pre;
            
            Window window;
            
                // Chain(blocks=[Window(length=1.0s, shift=0.25s, features=[Moments(), Autocorrelation(lag=1), Peaks(magnitude=0.1), CountAboveMean()]), Select(columns=['moments:min(my)', 'moments:std(my)', 'moments:max(mz)', 'moments:max(abs(mz))', 'moments:std(mz)', 'autocorrelation(mx)', 'autocorrelation(mz)', 'count_above_mean(mz)']), RandomForestClassifier(max_depth=7, min_samples_leaf=5, n_estimators=5)])
                _9wtN79__binarychain_135010442705232_8438152669077 chain1;
            
                // Chain(blocks=[Window(length=1.0s, shift=0.25s, features=[Moments(), Autocorrelation(lag=1), Peaks(magnitude=0.1), CountAboveMean()]), Select(columns=['moments:min(mz)', 'moments:max(mz)', 'moments:max(abs(mz))', 'autocorrelation(mz)', 'peaks(my)', 'peaks(mz)', 'count_above_mean(mx)', 'count_above_mean(mz)']), RandomForestClassifier(max_depth=7, min_samples_leaf=5, n_estimators=5)])
                _ZNFaTj__binarychain_135010413492112_8438150843257 chain2;
            
                // Chain(blocks=[Window(length=1.0s, shift=0.25s, features=[Moments(), Autocorrelation(lag=1), Peaks(magnitude=0.1), CountAboveMean()]), Select(columns=['moments:std(my)', 'moments:max(mz)', 'moments:mean(mz)', 'moments:max(abs(mz))', 'moments:mean(abs(mz))', 'count_above_mean(mx)', 'count_above_mean(my)', 'count_above_mean(mz)']), RandomForestClassifier(max_depth=7, min_samples_leaf=5, n_estimators=5)])
                _3cnwH0__binarychain_135010440334096_8438152520881 chain3;
            

            String getLabel(int8_t idx) {
                switch (idx) {
                    
                    default: return "unknown";
                }
            }
     };
}