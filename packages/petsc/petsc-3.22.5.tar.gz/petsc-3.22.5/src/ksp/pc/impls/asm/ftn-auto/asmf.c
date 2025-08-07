#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* asm.c */
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

#include "petscpc.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcasmsetlocalsubdomains_ PCASMSETLOCALSUBDOMAINS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcasmsetlocalsubdomains_ pcasmsetlocalsubdomains
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcasmsettotalsubdomains_ PCASMSETTOTALSUBDOMAINS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcasmsettotalsubdomains_ pcasmsettotalsubdomains
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcasmsetoverlap_ PCASMSETOVERLAP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcasmsetoverlap_ pcasmsetoverlap
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcasmsettype_ PCASMSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcasmsettype_ pcasmsettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcasmgettype_ PCASMGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcasmgettype_ pcasmgettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcasmsetlocaltype_ PCASMSETLOCALTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcasmsetlocaltype_ pcasmsetlocaltype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcasmgetlocaltype_ PCASMGETLOCALTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcasmgetlocaltype_ pcasmgetlocaltype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcasmsetsortindices_ PCASMSETSORTINDICES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcasmsetsortindices_ pcasmsetsortindices
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcasmsetdmsubdomains_ PCASMSETDMSUBDOMAINS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcasmsetdmsubdomains_ pcasmsetdmsubdomains
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcasmgetdmsubdomains_ PCASMGETDMSUBDOMAINS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcasmgetdmsubdomains_ pcasmgetdmsubdomains
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcasmgetsubmattype_ PCASMGETSUBMATTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcasmgetsubmattype_ pcasmgetsubmattype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcasmsetsubmattype_ PCASMSETSUBMATTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcasmsetsubmattype_ pcasmsetsubmattype
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  pcasmsetlocalsubdomains_(PC pc,PetscInt *n,IS is[],IS is_local[], int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
PetscBool is_null = !*(void**) is ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(is);
PetscBool is_local_null = !*(void**) is_local ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(is_local);
*ierr = PCASMSetLocalSubdomains(
	(PC)PetscToPointer((pc) ),*n,is,is_local);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! is_null && !*(void**) is) * (void **) is = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! is_local_null && !*(void**) is_local) * (void **) is_local = (void *)-2;
}
PETSC_EXTERN void  pcasmsettotalsubdomains_(PC pc,PetscInt *N,IS is[],IS is_local[], int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
PetscBool is_null = !*(void**) is ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(is);
PetscBool is_local_null = !*(void**) is_local ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(is_local);
*ierr = PCASMSetTotalSubdomains(
	(PC)PetscToPointer((pc) ),*N,is,is_local);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! is_null && !*(void**) is) * (void **) is = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! is_local_null && !*(void**) is_local) * (void **) is_local = (void *)-2;
}
PETSC_EXTERN void  pcasmsetoverlap_(PC pc,PetscInt *ovl, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCASMSetOverlap(
	(PC)PetscToPointer((pc) ),*ovl);
}
PETSC_EXTERN void  pcasmsettype_(PC pc,PCASMType *type, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCASMSetType(
	(PC)PetscToPointer((pc) ),*type);
}
PETSC_EXTERN void  pcasmgettype_(PC pc,PCASMType *type, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCASMGetType(
	(PC)PetscToPointer((pc) ),type);
}
PETSC_EXTERN void  pcasmsetlocaltype_(PC pc,PCCompositeType *type, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCASMSetLocalType(
	(PC)PetscToPointer((pc) ),*type);
}
PETSC_EXTERN void  pcasmgetlocaltype_(PC pc,PCCompositeType *type, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCASMGetLocalType(
	(PC)PetscToPointer((pc) ),type);
}
PETSC_EXTERN void  pcasmsetsortindices_(PC pc,PetscBool *doSort, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCASMSetSortIndices(
	(PC)PetscToPointer((pc) ),*doSort);
}
PETSC_EXTERN void  pcasmsetdmsubdomains_(PC pc,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCASMSetDMSubdomains(
	(PC)PetscToPointer((pc) ),*flg);
}
PETSC_EXTERN void  pcasmgetdmsubdomains_(PC pc,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCASMGetDMSubdomains(
	(PC)PetscToPointer((pc) ),flg);
}
PETSC_EXTERN void  pcasmgetsubmattype_(PC pc,char *sub_mat_type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(pc);
*ierr = PCASMGetSubMatType(
	(PC)PetscToPointer((pc) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for sub_mat_type */
*ierr = PetscStrncpy(sub_mat_type, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, sub_mat_type, cl0);
}
PETSC_EXTERN void  pcasmsetsubmattype_(PC pc,char *sub_mat_type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(pc);
/* insert Fortran-to-C conversion for sub_mat_type */
  FIXCHAR(sub_mat_type,cl0,_cltmp0);
*ierr = PCASMSetSubMatType(
	(PC)PetscToPointer((pc) ),_cltmp0);
  FREECHAR(sub_mat_type,_cltmp0);
}
#if defined(__cplusplus)
}
#endif
