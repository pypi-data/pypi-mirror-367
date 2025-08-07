#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* vector.c */
/* Fortran interface file */

/*
* This file was generated automatically by bfort from the C source
* file.  
 */

#ifdef PETSC_USE_POINTER_CONVERSION
#if defined(__cplusplus)
extern "C" { 
#endif 
extern void *PetscToPointer(void*);
extern int PetscFromPointer(void *);
extern void PetscRmPointer(void*);
#if defined(__cplusplus)
} 
#endif 

#else

#define PetscToPointer(a) (a ? *(PetscFortranAddr *)(a) : 0)
#define PetscFromPointer(a) (PetscFortranAddr)(a)
#define PetscRmPointer(a)
#endif

#include "petscvec.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecstashgetinfo_ VECSTASHGETINFO
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecstashgetinfo_ vecstashgetinfo
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecsetlocaltoglobalmapping_ VECSETLOCALTOGLOBALMAPPING
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecsetlocaltoglobalmapping_ vecsetlocaltoglobalmapping
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecgetlocaltoglobalmapping_ VECGETLOCALTOGLOBALMAPPING
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecgetlocaltoglobalmapping_ vecgetlocaltoglobalmapping
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecassemblybegin_ VECASSEMBLYBEGIN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecassemblybegin_ vecassemblybegin
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecassemblyend_ VECASSEMBLYEND
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecassemblyend_ vecassemblyend
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecsetpreallocationcoo_ VECSETPREALLOCATIONCOO
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecsetpreallocationcoo_ vecsetpreallocationcoo
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecsetpreallocationcoolocal_ VECSETPREALLOCATIONCOOLOCAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecsetpreallocationcoolocal_ vecsetpreallocationcoolocal
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecsetvaluescoo_ VECSETVALUESCOO
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecsetvaluescoo_ vecsetvaluescoo
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecpointwisemax_ VECPOINTWISEMAX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecpointwisemax_ vecpointwisemax
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecpointwisemin_ VECPOINTWISEMIN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecpointwisemin_ vecpointwisemin
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecpointwisemaxabs_ VECPOINTWISEMAXABS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecpointwisemaxabs_ vecpointwisemaxabs
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecpointwisedivide_ VECPOINTWISEDIVIDE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecpointwisedivide_ vecpointwisedivide
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecpointwisemult_ VECPOINTWISEMULT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecpointwisemult_ vecpointwisemult
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecduplicate_ VECDUPLICATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecduplicate_ vecduplicate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecdestroy_ VECDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecdestroy_ vecdestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecviewfromoptions_ VECVIEWFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecviewfromoptions_ vecviewfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecview_ VECVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecview_ vecview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecgetsize_ VECGETSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecgetsize_ vecgetsize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecgetlocalsize_ VECGETLOCALSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecgetlocalsize_ vecgetlocalsize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecgetownershiprange_ VECGETOWNERSHIPRANGE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecgetownershiprange_ vecgetownershiprange
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecsetoption_ VECSETOPTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecsetoption_ vecsetoption
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecresetarray_ VECRESETARRAY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecresetarray_ vecresetarray
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecload_ VECLOAD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecload_ vecload
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecreciprocal_ VECRECIPROCAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecreciprocal_ vecreciprocal
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecstashsetinitialsize_ VECSTASHSETINITIALSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecstashsetinitialsize_ vecstashsetinitialsize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecsetrandom_ VECSETRANDOM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecsetrandom_ vecsetrandom
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define veczeroentries_ VECZEROENTRIES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define veczeroentries_ veczeroentries
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecsetfromoptions_ VECSETFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecsetfromoptions_ vecsetfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecsetsizes_ VECSETSIZES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecsetsizes_ vecsetsizes
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecsetblocksize_ VECSETBLOCKSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecsetblocksize_ vecsetblocksize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecgetblocksize_ VECGETBLOCKSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecgetblocksize_ vecgetblocksize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecsetoptionsprefix_ VECSETOPTIONSPREFIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecsetoptionsprefix_ vecsetoptionsprefix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecappendoptionsprefix_ VECAPPENDOPTIONSPREFIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecappendoptionsprefix_ vecappendoptionsprefix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecgetoptionsprefix_ VECGETOPTIONSPREFIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecgetoptionsprefix_ vecgetoptionsprefix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecsetup_ VECSETUP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecsetup_ vecsetup
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define veccopy_ VECCOPY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define veccopy_ veccopy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecswap_ VECSWAP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecswap_ vecswap
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecstashviewfromoptions_ VECSTASHVIEWFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecstashviewfromoptions_ vecstashviewfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecstashview_ VECSTASHVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecstashview_ vecstashview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecgetlayout_ VECGETLAYOUT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecgetlayout_ vecgetlayout
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecsetlayout_ VECSETLAYOUT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecsetlayout_ vecsetlayout
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecflag_ VECFLAG
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecflag_ vecflag
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecsetinf_ VECSETINF
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecsetinf_ vecsetinf
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecbindtocpu_ VECBINDTOCPU
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecbindtocpu_ vecbindtocpu
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecboundtocpu_ VECBOUNDTOCPU
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecboundtocpu_ vecboundtocpu
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecsetbindingpropagates_ VECSETBINDINGPROPAGATES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecsetbindingpropagates_ vecsetbindingpropagates
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecgetbindingpropagates_ VECGETBINDINGPROPAGATES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecgetbindingpropagates_ vecgetbindingpropagates
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecgetoffloadmask_ VECGETOFFLOADMASK
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecgetoffloadmask_ vecgetoffloadmask
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecerrorweightednorms_ VECERRORWEIGHTEDNORMS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecerrorweightednorms_ vecerrorweightednorms
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  vecstashgetinfo_(Vec vec,PetscInt *nstash,PetscInt *reallocs,PetscInt *bnstash,PetscInt *breallocs, int *ierr)
{
CHKFORTRANNULLOBJECT(vec);
CHKFORTRANNULLINTEGER(nstash);
CHKFORTRANNULLINTEGER(reallocs);
CHKFORTRANNULLINTEGER(bnstash);
CHKFORTRANNULLINTEGER(breallocs);
*ierr = VecStashGetInfo(
	(Vec)PetscToPointer((vec) ),nstash,reallocs,bnstash,breallocs);
}
PETSC_EXTERN void  vecsetlocaltoglobalmapping_(Vec x,ISLocalToGlobalMapping mapping, int *ierr)
{
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(mapping);
*ierr = VecSetLocalToGlobalMapping(
	(Vec)PetscToPointer((x) ),
	(ISLocalToGlobalMapping)PetscToPointer((mapping) ));
}
PETSC_EXTERN void  vecgetlocaltoglobalmapping_(Vec X,ISLocalToGlobalMapping *mapping, int *ierr)
{
CHKFORTRANNULLOBJECT(X);
PetscBool mapping_null = !*(void**) mapping ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(mapping);
*ierr = VecGetLocalToGlobalMapping(
	(Vec)PetscToPointer((X) ),mapping);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! mapping_null && !*(void**) mapping) * (void **) mapping = (void *)-2;
}
PETSC_EXTERN void  vecassemblybegin_(Vec vec, int *ierr)
{
CHKFORTRANNULLOBJECT(vec);
*ierr = VecAssemblyBegin(
	(Vec)PetscToPointer((vec) ));
}
PETSC_EXTERN void  vecassemblyend_(Vec vec, int *ierr)
{
CHKFORTRANNULLOBJECT(vec);
*ierr = VecAssemblyEnd(
	(Vec)PetscToPointer((vec) ));
}
PETSC_EXTERN void  vecsetpreallocationcoo_(Vec x,PetscCount *ncoo, PetscInt coo_i[], int *ierr)
{
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLINTEGER(coo_i);
*ierr = VecSetPreallocationCOO(
	(Vec)PetscToPointer((x) ),*ncoo,coo_i);
}
PETSC_EXTERN void  vecsetpreallocationcoolocal_(Vec x,PetscCount *ncoo,PetscInt coo_i[], int *ierr)
{
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLINTEGER(coo_i);
*ierr = VecSetPreallocationCOOLocal(
	(Vec)PetscToPointer((x) ),*ncoo,coo_i);
}
PETSC_EXTERN void  vecsetvaluescoo_(Vec x, PetscScalar coo_v[],InsertMode *imode, int *ierr)
{
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLSCALAR(coo_v);
*ierr = VecSetValuesCOO(
	(Vec)PetscToPointer((x) ),coo_v,*imode);
}
PETSC_EXTERN void  vecpointwisemax_(Vec w,Vec x,Vec y, int *ierr)
{
CHKFORTRANNULLOBJECT(w);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(y);
*ierr = VecPointwiseMax(
	(Vec)PetscToPointer((w) ),
	(Vec)PetscToPointer((x) ),
	(Vec)PetscToPointer((y) ));
}
PETSC_EXTERN void  vecpointwisemin_(Vec w,Vec x,Vec y, int *ierr)
{
CHKFORTRANNULLOBJECT(w);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(y);
*ierr = VecPointwiseMin(
	(Vec)PetscToPointer((w) ),
	(Vec)PetscToPointer((x) ),
	(Vec)PetscToPointer((y) ));
}
PETSC_EXTERN void  vecpointwisemaxabs_(Vec w,Vec x,Vec y, int *ierr)
{
CHKFORTRANNULLOBJECT(w);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(y);
*ierr = VecPointwiseMaxAbs(
	(Vec)PetscToPointer((w) ),
	(Vec)PetscToPointer((x) ),
	(Vec)PetscToPointer((y) ));
}
PETSC_EXTERN void  vecpointwisedivide_(Vec w,Vec x,Vec y, int *ierr)
{
CHKFORTRANNULLOBJECT(w);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(y);
*ierr = VecPointwiseDivide(
	(Vec)PetscToPointer((w) ),
	(Vec)PetscToPointer((x) ),
	(Vec)PetscToPointer((y) ));
}
PETSC_EXTERN void  vecpointwisemult_(Vec w,Vec x,Vec y, int *ierr)
{
CHKFORTRANNULLOBJECT(w);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(y);
*ierr = VecPointwiseMult(
	(Vec)PetscToPointer((w) ),
	(Vec)PetscToPointer((x) ),
	(Vec)PetscToPointer((y) ));
}
PETSC_EXTERN void  vecduplicate_(Vec v,Vec *newv, int *ierr)
{
CHKFORTRANNULLOBJECT(v);
PetscBool newv_null = !*(void**) newv ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(newv);
*ierr = VecDuplicate(
	(Vec)PetscToPointer((v) ),newv);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! newv_null && !*(void**) newv) * (void **) newv = (void *)-2;
}
PETSC_EXTERN void  vecdestroy_(Vec *v, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(v);
 PetscBool v_null = !*(void**) v ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(v);
*ierr = VecDestroy(v);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! v_null && !*(void**) v) * (void **) v = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(v);
 }
PETSC_EXTERN void  vecviewfromoptions_(Vec A,PetscObject obj, char name[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(obj);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = VecViewFromOptions(
	(Vec)PetscToPointer((A) ),
	(PetscObject)PetscToPointer((obj) ),_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  vecview_(Vec vec,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(vec);
CHKFORTRANNULLOBJECT(viewer);
*ierr = VecView(
	(Vec)PetscToPointer((vec) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  vecgetsize_(Vec x,PetscInt *size, int *ierr)
{
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLINTEGER(size);
*ierr = VecGetSize(
	(Vec)PetscToPointer((x) ),size);
}
PETSC_EXTERN void  vecgetlocalsize_(Vec x,PetscInt *size, int *ierr)
{
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLINTEGER(size);
*ierr = VecGetLocalSize(
	(Vec)PetscToPointer((x) ),size);
}
PETSC_EXTERN void  vecgetownershiprange_(Vec x,PetscInt *low,PetscInt *high, int *ierr)
{
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLINTEGER(low);
CHKFORTRANNULLINTEGER(high);
*ierr = VecGetOwnershipRange(
	(Vec)PetscToPointer((x) ),low,high);
}
PETSC_EXTERN void  vecsetoption_(Vec x,VecOption *op,PetscBool *flag, int *ierr)
{
CHKFORTRANNULLOBJECT(x);
*ierr = VecSetOption(
	(Vec)PetscToPointer((x) ),*op,*flag);
}
PETSC_EXTERN void  vecresetarray_(Vec vec, int *ierr)
{
CHKFORTRANNULLOBJECT(vec);
*ierr = VecResetArray(
	(Vec)PetscToPointer((vec) ));
}
PETSC_EXTERN void  vecload_(Vec vec,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(vec);
CHKFORTRANNULLOBJECT(viewer);
*ierr = VecLoad(
	(Vec)PetscToPointer((vec) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  vecreciprocal_(Vec vec, int *ierr)
{
CHKFORTRANNULLOBJECT(vec);
*ierr = VecReciprocal(
	(Vec)PetscToPointer((vec) ));
}
PETSC_EXTERN void  vecstashsetinitialsize_(Vec vec,PetscInt *size,PetscInt *bsize, int *ierr)
{
CHKFORTRANNULLOBJECT(vec);
*ierr = VecStashSetInitialSize(
	(Vec)PetscToPointer((vec) ),*size,*bsize);
}
PETSC_EXTERN void  vecsetrandom_(Vec x,PetscRandom rctx, int *ierr)
{
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(rctx);
*ierr = VecSetRandom(
	(Vec)PetscToPointer((x) ),
	(PetscRandom)PetscToPointer((rctx) ));
}
PETSC_EXTERN void  veczeroentries_(Vec vec, int *ierr)
{
CHKFORTRANNULLOBJECT(vec);
*ierr = VecZeroEntries(
	(Vec)PetscToPointer((vec) ));
}
PETSC_EXTERN void  vecsetfromoptions_(Vec vec, int *ierr)
{
CHKFORTRANNULLOBJECT(vec);
*ierr = VecSetFromOptions(
	(Vec)PetscToPointer((vec) ));
}
PETSC_EXTERN void  vecsetsizes_(Vec v,PetscInt *n,PetscInt *N, int *ierr)
{
CHKFORTRANNULLOBJECT(v);
*ierr = VecSetSizes(
	(Vec)PetscToPointer((v) ),*n,*N);
}
PETSC_EXTERN void  vecsetblocksize_(Vec v,PetscInt *bs, int *ierr)
{
CHKFORTRANNULLOBJECT(v);
*ierr = VecSetBlockSize(
	(Vec)PetscToPointer((v) ),*bs);
}
PETSC_EXTERN void  vecgetblocksize_(Vec v,PetscInt *bs, int *ierr)
{
CHKFORTRANNULLOBJECT(v);
CHKFORTRANNULLINTEGER(bs);
*ierr = VecGetBlockSize(
	(Vec)PetscToPointer((v) ),bs);
}
PETSC_EXTERN void  vecsetoptionsprefix_(Vec v, char prefix[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(v);
/* insert Fortran-to-C conversion for prefix */
  FIXCHAR(prefix,cl0,_cltmp0);
*ierr = VecSetOptionsPrefix(
	(Vec)PetscToPointer((v) ),_cltmp0);
  FREECHAR(prefix,_cltmp0);
}
PETSC_EXTERN void  vecappendoptionsprefix_(Vec v, char prefix[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(v);
/* insert Fortran-to-C conversion for prefix */
  FIXCHAR(prefix,cl0,_cltmp0);
*ierr = VecAppendOptionsPrefix(
	(Vec)PetscToPointer((v) ),_cltmp0);
  FREECHAR(prefix,_cltmp0);
}
PETSC_EXTERN void  vecgetoptionsprefix_(Vec v, char *prefix, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(v);
*ierr = VecGetOptionsPrefix(
	(Vec)PetscToPointer((v) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for prefix */
*ierr = PetscStrncpy(prefix, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, prefix, cl0);
}
PETSC_EXTERN void  vecsetup_(Vec v, int *ierr)
{
CHKFORTRANNULLOBJECT(v);
*ierr = VecSetUp(
	(Vec)PetscToPointer((v) ));
}
PETSC_EXTERN void  veccopy_(Vec x,Vec y, int *ierr)
{
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(y);
*ierr = VecCopy(
	(Vec)PetscToPointer((x) ),
	(Vec)PetscToPointer((y) ));
}
PETSC_EXTERN void  vecswap_(Vec x,Vec y, int *ierr)
{
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(y);
*ierr = VecSwap(
	(Vec)PetscToPointer((x) ),
	(Vec)PetscToPointer((y) ));
}
PETSC_EXTERN void  vecstashviewfromoptions_(Vec obj,PetscObject bobj, char optionname[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(obj);
CHKFORTRANNULLOBJECT(bobj);
/* insert Fortran-to-C conversion for optionname */
  FIXCHAR(optionname,cl0,_cltmp0);
*ierr = VecStashViewFromOptions(
	(Vec)PetscToPointer((obj) ),
	(PetscObject)PetscToPointer((bobj) ),_cltmp0);
  FREECHAR(optionname,_cltmp0);
}
PETSC_EXTERN void  vecstashview_(Vec v,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(v);
CHKFORTRANNULLOBJECT(viewer);
*ierr = VecStashView(
	(Vec)PetscToPointer((v) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  vecgetlayout_(Vec x,PetscLayout *map, int *ierr)
{
CHKFORTRANNULLOBJECT(x);
PetscBool map_null = !*(void**) map ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(map);
*ierr = VecGetLayout(
	(Vec)PetscToPointer((x) ),map);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! map_null && !*(void**) map) * (void **) map = (void *)-2;
}
PETSC_EXTERN void  vecsetlayout_(Vec x,PetscLayout map, int *ierr)
{
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(map);
*ierr = VecSetLayout(
	(Vec)PetscToPointer((x) ),
	(PetscLayout)PetscToPointer((map) ));
}
PETSC_EXTERN void  vecflag_(Vec xin,PetscInt *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(xin);
*ierr = VecFlag(
	(Vec)PetscToPointer((xin) ),*flg);
}
PETSC_EXTERN void  vecsetinf_(Vec xin, int *ierr)
{
CHKFORTRANNULLOBJECT(xin);
*ierr = VecSetInf(
	(Vec)PetscToPointer((xin) ));
}
PETSC_EXTERN void  vecbindtocpu_(Vec v,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(v);
*ierr = VecBindToCPU(
	(Vec)PetscToPointer((v) ),*flg);
}
PETSC_EXTERN void  vecboundtocpu_(Vec v,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(v);
*ierr = VecBoundToCPU(
	(Vec)PetscToPointer((v) ),flg);
}
PETSC_EXTERN void  vecsetbindingpropagates_(Vec v,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(v);
*ierr = VecSetBindingPropagates(
	(Vec)PetscToPointer((v) ),*flg);
}
PETSC_EXTERN void  vecgetbindingpropagates_(Vec v,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(v);
*ierr = VecGetBindingPropagates(
	(Vec)PetscToPointer((v) ),flg);
}
PETSC_EXTERN void  vecgetoffloadmask_(Vec v,PetscOffloadMask *mask, int *ierr)
{
CHKFORTRANNULLOBJECT(v);
*ierr = VecGetOffloadMask(
	(Vec)PetscToPointer((v) ),mask);
}
PETSC_EXTERN void  vecerrorweightednorms_(Vec U,Vec Y,Vec E,NormType *wnormtype,PetscReal *atol,Vec vatol,PetscReal *rtol,Vec vrtol,PetscReal *ignore_max,PetscReal *norm,PetscInt *norm_loc,PetscReal *norma,PetscInt *norma_loc,PetscReal *normr,PetscInt *normr_loc, int *ierr)
{
CHKFORTRANNULLOBJECT(U);
CHKFORTRANNULLOBJECT(Y);
CHKFORTRANNULLOBJECT(E);
CHKFORTRANNULLOBJECT(vatol);
CHKFORTRANNULLOBJECT(vrtol);
CHKFORTRANNULLREAL(norm);
CHKFORTRANNULLINTEGER(norm_loc);
CHKFORTRANNULLREAL(norma);
CHKFORTRANNULLINTEGER(norma_loc);
CHKFORTRANNULLREAL(normr);
CHKFORTRANNULLINTEGER(normr_loc);
*ierr = VecErrorWeightedNorms(
	(Vec)PetscToPointer((U) ),
	(Vec)PetscToPointer((Y) ),
	(Vec)PetscToPointer((E) ),*wnormtype,*atol,
	(Vec)PetscToPointer((vatol) ),*rtol,
	(Vec)PetscToPointer((vrtol) ),*ignore_max,norm,norm_loc,norma,norma_loc,normr,normr_loc);
}
#if defined(__cplusplus)
}
#endif
