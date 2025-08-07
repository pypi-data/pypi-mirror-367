#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* fieldsplit.c */
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
#define pcfieldsplitrestrictis_ PCFIELDSPLITRESTRICTIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfieldsplitrestrictis_ pcfieldsplitrestrictis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfieldsplitsetfields_ PCFIELDSPLITSETFIELDS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfieldsplitsetfields_ pcfieldsplitsetfields
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfieldsplitsetdiaguseamat_ PCFIELDSPLITSETDIAGUSEAMAT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfieldsplitsetdiaguseamat_ pcfieldsplitsetdiaguseamat
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfieldsplitgetdiaguseamat_ PCFIELDSPLITGETDIAGUSEAMAT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfieldsplitgetdiaguseamat_ pcfieldsplitgetdiaguseamat
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfieldsplitsetoffdiaguseamat_ PCFIELDSPLITSETOFFDIAGUSEAMAT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfieldsplitsetoffdiaguseamat_ pcfieldsplitsetoffdiaguseamat
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfieldsplitgetoffdiaguseamat_ PCFIELDSPLITGETOFFDIAGUSEAMAT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfieldsplitgetoffdiaguseamat_ pcfieldsplitgetoffdiaguseamat
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfieldsplitsetis_ PCFIELDSPLITSETIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfieldsplitsetis_ pcfieldsplitsetis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfieldsplitgetis_ PCFIELDSPLITGETIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfieldsplitgetis_ pcfieldsplitgetis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfieldsplitgetisbyindex_ PCFIELDSPLITGETISBYINDEX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfieldsplitgetisbyindex_ pcfieldsplitgetisbyindex
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfieldsplitsetblocksize_ PCFIELDSPLITSETBLOCKSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfieldsplitsetblocksize_ pcfieldsplitsetblocksize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfieldsplitsetschurpre_ PCFIELDSPLITSETSCHURPRE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfieldsplitsetschurpre_ pcfieldsplitsetschurpre
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfieldsplitgetschurpre_ PCFIELDSPLITGETSCHURPRE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfieldsplitgetschurpre_ pcfieldsplitgetschurpre
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfieldsplitschurgets_ PCFIELDSPLITSCHURGETS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfieldsplitschurgets_ pcfieldsplitschurgets
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfieldsplitschurrestores_ PCFIELDSPLITSCHURRESTORES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfieldsplitschurrestores_ pcfieldsplitschurrestores
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfieldsplitsetschurfacttype_ PCFIELDSPLITSETSCHURFACTTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfieldsplitsetschurfacttype_ pcfieldsplitsetschurfacttype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfieldsplitsetschurscale_ PCFIELDSPLITSETSCHURSCALE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfieldsplitsetschurscale_ pcfieldsplitsetschurscale
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfieldsplitsetgkbtol_ PCFIELDSPLITSETGKBTOL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfieldsplitsetgkbtol_ pcfieldsplitsetgkbtol
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfieldsplitsetgkbmaxit_ PCFIELDSPLITSETGKBMAXIT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfieldsplitsetgkbmaxit_ pcfieldsplitsetgkbmaxit
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfieldsplitsetgkbdelay_ PCFIELDSPLITSETGKBDELAY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfieldsplitsetgkbdelay_ pcfieldsplitsetgkbdelay
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfieldsplitsetgkbnu_ PCFIELDSPLITSETGKBNU
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfieldsplitsetgkbnu_ pcfieldsplitsetgkbnu
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfieldsplitsettype_ PCFIELDSPLITSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfieldsplitsettype_ pcfieldsplitsettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfieldsplitgettype_ PCFIELDSPLITGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfieldsplitgettype_ pcfieldsplitgettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfieldsplitsetdmsplits_ PCFIELDSPLITSETDMSPLITS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfieldsplitsetdmsplits_ pcfieldsplitsetdmsplits
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfieldsplitgetdmsplits_ PCFIELDSPLITGETDMSPLITS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfieldsplitgetdmsplits_ pcfieldsplitgetdmsplits
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfieldsplitgetdetectsaddlepoint_ PCFIELDSPLITGETDETECTSADDLEPOINT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfieldsplitgetdetectsaddlepoint_ pcfieldsplitgetdetectsaddlepoint
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfieldsplitsetdetectsaddlepoint_ PCFIELDSPLITSETDETECTSADDLEPOINT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfieldsplitsetdetectsaddlepoint_ pcfieldsplitsetdetectsaddlepoint
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  pcfieldsplitrestrictis_(PC pc,IS isy, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(isy);
*ierr = PCFieldSplitRestrictIS(
	(PC)PetscToPointer((pc) ),
	(IS)PetscToPointer((isy) ));
}
PETSC_EXTERN void  pcfieldsplitsetfields_(PC pc, char splitname[],PetscInt *n, PetscInt fields[], PetscInt fields_col[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLINTEGER(fields);
CHKFORTRANNULLINTEGER(fields_col);
/* insert Fortran-to-C conversion for splitname */
  FIXCHAR(splitname,cl0,_cltmp0);
*ierr = PCFieldSplitSetFields(
	(PC)PetscToPointer((pc) ),_cltmp0,*n,fields,fields_col);
  FREECHAR(splitname,_cltmp0);
}
PETSC_EXTERN void  pcfieldsplitsetdiaguseamat_(PC pc,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCFieldSplitSetDiagUseAmat(
	(PC)PetscToPointer((pc) ),*flg);
}
PETSC_EXTERN void  pcfieldsplitgetdiaguseamat_(PC pc,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCFieldSplitGetDiagUseAmat(
	(PC)PetscToPointer((pc) ),flg);
}
PETSC_EXTERN void  pcfieldsplitsetoffdiaguseamat_(PC pc,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCFieldSplitSetOffDiagUseAmat(
	(PC)PetscToPointer((pc) ),*flg);
}
PETSC_EXTERN void  pcfieldsplitgetoffdiaguseamat_(PC pc,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCFieldSplitGetOffDiagUseAmat(
	(PC)PetscToPointer((pc) ),flg);
}
PETSC_EXTERN void  pcfieldsplitsetis_(PC pc, char splitname[],IS is, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(is);
/* insert Fortran-to-C conversion for splitname */
  FIXCHAR(splitname,cl0,_cltmp0);
*ierr = PCFieldSplitSetIS(
	(PC)PetscToPointer((pc) ),_cltmp0,
	(IS)PetscToPointer((is) ));
  FREECHAR(splitname,_cltmp0);
}
PETSC_EXTERN void  pcfieldsplitgetis_(PC pc, char splitname[],IS *is, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(pc);
PetscBool is_null = !*(void**) is ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(is);
/* insert Fortran-to-C conversion for splitname */
  FIXCHAR(splitname,cl0,_cltmp0);
*ierr = PCFieldSplitGetIS(
	(PC)PetscToPointer((pc) ),_cltmp0,is);
  FREECHAR(splitname,_cltmp0);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! is_null && !*(void**) is) * (void **) is = (void *)-2;
}
PETSC_EXTERN void  pcfieldsplitgetisbyindex_(PC pc,PetscInt *index,IS *is, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
PetscBool is_null = !*(void**) is ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(is);
*ierr = PCFieldSplitGetISByIndex(
	(PC)PetscToPointer((pc) ),*index,is);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! is_null && !*(void**) is) * (void **) is = (void *)-2;
}
PETSC_EXTERN void  pcfieldsplitsetblocksize_(PC pc,PetscInt *bs, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCFieldSplitSetBlockSize(
	(PC)PetscToPointer((pc) ),*bs);
}
PETSC_EXTERN void  pcfieldsplitsetschurpre_(PC pc,PCFieldSplitSchurPreType *ptype,Mat pre, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(pre);
*ierr = PCFieldSplitSetSchurPre(
	(PC)PetscToPointer((pc) ),*ptype,
	(Mat)PetscToPointer((pre) ));
}
PETSC_EXTERN void  pcfieldsplitgetschurpre_(PC pc,PCFieldSplitSchurPreType *ptype,Mat *pre, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
PetscBool pre_null = !*(void**) pre ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(pre);
*ierr = PCFieldSplitGetSchurPre(
	(PC)PetscToPointer((pc) ),ptype,pre);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! pre_null && !*(void**) pre) * (void **) pre = (void *)-2;
}
PETSC_EXTERN void  pcfieldsplitschurgets_(PC pc,Mat *S, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
PetscBool S_null = !*(void**) S ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(S);
*ierr = PCFieldSplitSchurGetS(
	(PC)PetscToPointer((pc) ),S);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! S_null && !*(void**) S) * (void **) S = (void *)-2;
}
PETSC_EXTERN void  pcfieldsplitschurrestores_(PC pc,Mat *S, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
PetscBool S_null = !*(void**) S ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(S);
*ierr = PCFieldSplitSchurRestoreS(
	(PC)PetscToPointer((pc) ),S);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! S_null && !*(void**) S) * (void **) S = (void *)-2;
}
PETSC_EXTERN void  pcfieldsplitsetschurfacttype_(PC pc,PCFieldSplitSchurFactType *ftype, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCFieldSplitSetSchurFactType(
	(PC)PetscToPointer((pc) ),*ftype);
}
PETSC_EXTERN void  pcfieldsplitsetschurscale_(PC pc,PetscScalar *scale, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCFieldSplitSetSchurScale(
	(PC)PetscToPointer((pc) ),*scale);
}
PETSC_EXTERN void  pcfieldsplitsetgkbtol_(PC pc,PetscReal *tolerance, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCFieldSplitSetGKBTol(
	(PC)PetscToPointer((pc) ),*tolerance);
}
PETSC_EXTERN void  pcfieldsplitsetgkbmaxit_(PC pc,PetscInt *maxit, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCFieldSplitSetGKBMaxit(
	(PC)PetscToPointer((pc) ),*maxit);
}
PETSC_EXTERN void  pcfieldsplitsetgkbdelay_(PC pc,PetscInt *delay, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCFieldSplitSetGKBDelay(
	(PC)PetscToPointer((pc) ),*delay);
}
PETSC_EXTERN void  pcfieldsplitsetgkbnu_(PC pc,PetscReal *nu, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCFieldSplitSetGKBNu(
	(PC)PetscToPointer((pc) ),*nu);
}
PETSC_EXTERN void  pcfieldsplitsettype_(PC pc,PCCompositeType *type, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCFieldSplitSetType(
	(PC)PetscToPointer((pc) ),*type);
}
PETSC_EXTERN void  pcfieldsplitgettype_(PC pc,PCCompositeType *type, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCFieldSplitGetType(
	(PC)PetscToPointer((pc) ),type);
}
PETSC_EXTERN void  pcfieldsplitsetdmsplits_(PC pc,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCFieldSplitSetDMSplits(
	(PC)PetscToPointer((pc) ),*flg);
}
PETSC_EXTERN void  pcfieldsplitgetdmsplits_(PC pc,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCFieldSplitGetDMSplits(
	(PC)PetscToPointer((pc) ),flg);
}
PETSC_EXTERN void  pcfieldsplitgetdetectsaddlepoint_(PC pc,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCFieldSplitGetDetectSaddlePoint(
	(PC)PetscToPointer((pc) ),flg);
}
PETSC_EXTERN void  pcfieldsplitsetdetectsaddlepoint_(PC pc,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCFieldSplitSetDetectSaddlePoint(
	(PC)PetscToPointer((pc) ),*flg);
}
#if defined(__cplusplus)
}
#endif
