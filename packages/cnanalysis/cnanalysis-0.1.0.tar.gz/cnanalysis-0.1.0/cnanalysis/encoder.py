import pandas as pd 
from sklearn.preprocessing import LabelEncoder,OneHotEncoder,OrdinalEncoder
from typing import List,Optional,Dict,Union
class EncodeCat:
    def __init__(self,
                 data:pd.DataFrame,
                 cat_cols:Optional[List[str]]=None,
                 method :str ="label",
                 ordinal_mapping :Optional[Dict[str, List[str]]] =None,
                 drop_first : bool=True,
                 inplace : bool =False
                 )->None:
        """
        Encode categorical columns using Label, One-Hot, or Ordinal encoding.

        Parameters:
        ----------
        df : pd.DataFrame
            Input DataFrame.

        cat_cols : list of str
            List of categorical column names to encode.

        method : str, optional (default='label')
            Encoding method: 'label', 'onehot', or 'ordinal'.

        ordinal_mapping : dict, optional
            Required only for 'ordinal' method. Dictionary of column-to-category-order mappings.

        drop_first : bool, optional (default=True)
            Whether to drop the first category in one-hot encoding to avoid multicollinearity.

        inplace : bool, optional (default=False)
            Whether to modify the DataFrame in place.
        """
        self.data=data
        self.cat_cols=cat_cols
        self.method=method.lower()
        self.ordinal_mapping=ordinal_mapping
        self.drop_first=drop_first
        self.inplace=inplace
    def encode(self)->pd.DataFrame:
        """Run EncodeCat and return result.

        Returns:
            pd.DataFrame: Encoded DataFrame.
        """
        try:
            if self.cat_cols is None:
                self.cat_cols =self._get_cat_col()
            if not self.inplace:
                self.data =self.data.copy()
            for col in self.cat_cols:
                if not pd.api.types.is_object_dtype(self.data[col]):
                    raise TypeError(f"The column : {col} should be categorical.")
                if col not in self.data.columns:
                    raise ValueError(f"The column :{col} is not present in data.")
                if self.method not in self._checkmethod():
                    raise ValueError(f"The method :'{self.method} is wrong.Encoding method must be one of: 'label', 'onehot', 'ordinal'.")
                if self.method =="label":
                    self.data[col]=LabelEncoder().fit_transform(self.data[col].astype(str))
                elif self.method =="onehot":
                    onehot=pd.get_dummies(self.data[col],prefix=col,drop_first=self.drop_first)
                    self.data.drop(columns=col,inplace=True)
                    self.data =pd.concat([self.data,onehot],axis=1)
                elif self.method =="ordinal":
                    if not self.ordinal_mapping or col not in self.ordinal_mapping:
                        raise ValueError(f"Ordinal mapping not provided for column '{col}'.")
                    encoder = OrdinalEncoder(categories=[self.ordinal_mapping[col]])
                    self.data[col]=encoder.fit_transform(self.data[[col]])
            return self.data
        except Exception as e:
            raise ValueError(f"Error occur when labelling :{e}")
    def _get_cat_col(self)->list[str]:
        return self.data.select_dtypes(include=['object','category']).columns.to_list()
    def _checkmethod(self)->list[str]:
        return ["label","onehot","ordinal"]